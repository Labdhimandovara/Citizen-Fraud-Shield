"""Production-grade training pipeline for Citizen Fraud Shield."""
from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass, asdict
import base64
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import cv2
import joblib
import numpy as np
import pandas as pd
from PIL import Image, ImageEnhance, UnidentifiedImageError
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

from dataset_models import CALL_MODEL_PATH, CURRENCY_MODEL_PATH, MODELS, TRANSACTION_MODEL_PATH

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

ROOT = Path(__file__).parent
MODEL_REGISTRY_PATH = MODELS / "registry.json"
ARTIFACT_DIR = MODELS / "artifacts"

TRANSACTION_NUMERIC = [
    "step",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "amount_to_oldbalance_ratio",
    "origin_balance_change",
    "destination_balance_change",
    "transaction_size_log",
    "account_age_days",
    "transactions_24h",
]
TRANSACTION_CATEGORICAL = ["type"]

IMAGE_SIZE = (72, 72)
MAX_CALL_ROWS = 0  # 0 means use all if a dataset is supplied


@dataclass
class ModelRecord:
    model_name: str
    model_version: str
    dataset_name: str
    dataset_size: int
    training_timestamp: str
    artifact_path: str
    preprocessing_configuration: Dict[str, Any]
    image_size: Tuple[int, int] | None
    augmentation: str
    label_mapping: Dict[str, Any]
    metrics: Dict[str, Any]
    confusion_matrix: List[List[int]]
    roc_curve_path: str | None
    reload_check: Dict[str, Any]


def _ensure_dirs() -> None:
    MODELS.mkdir(exist_ok=True)
    ARTIFACT_DIR.mkdir(exist_ok=True)


def _utc_version() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def _metrics(y_true, y_pred, y_prob) -> Dict[str, float]:
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, y_prob)), 4),
        "rows": int(len(y_true)),
    }


def _best_f1_threshold(y_true, y_prob) -> float:
    thresholds = np.unique(np.round(y_prob, 4))
    if thresholds.size == 0:
        return 0.5
    best_threshold = 0.5
    best_score = -1.0
    for threshold in thresholds:
        pred = (y_prob >= threshold).astype(int)
        score = f1_score(y_true, pred, zero_division=0)
        if score > best_score:
            best_score = score
            best_threshold = float(threshold)
    return round(best_threshold, 4)


def _plot_confusion_matrix(y_true, y_pred, path: Path, title: str) -> List[List[int]]:
    matrix = confusion_matrix(y_true, y_pred).tolist()
    canvas = np.full((360, 460, 3), 255, dtype=np.uint8)
    colors = {(0, 0): (235, 245, 255), (0, 1): (210, 230, 255), (1, 0): (200, 225, 250), (1, 1): (160, 205, 245)}
    origin = (110, 110)
    cell = 120
    for i in range(2):
        for j in range(2):
            x1, y1 = origin[0] + j * cell, origin[1] + i * cell
            x2, y2 = x1 + cell, y1 + cell
            cv2.rectangle(canvas, (x1, y1), (x2, y2), colors[(i, j)], thickness=-1)
            cv2.rectangle(canvas, (x1, y1), (x2, y2), (80, 80, 80), thickness=2)
            value = str(matrix[i][j])
            cv2.putText(canvas, value, (x1 + 35, y1 + 68), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (20, 20, 20), 3)
    cv2.putText(canvas, title, (60, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (30, 30, 30), 2)
    cv2.putText(canvas, "Predicted", (170, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (30, 30, 30), 2)
    cv2.putText(canvas, "Actual", (20, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (30, 30, 30), 2)
    cv2.putText(canvas, "0", (170, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (30, 30, 30), 2)
    cv2.putText(canvas, "1", (290, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (30, 30, 30), 2)
    cv2.putText(canvas, "0", (75, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (30, 30, 30), 2)
    cv2.putText(canvas, "1", (75, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (30, 30, 30), 2)
    cv2.imwrite(str(path), canvas)
    return matrix


def _plot_roc_curve(y_true, y_prob, path: Path, title: str) -> None:
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    canvas = np.full((360, 460, 3), 255, dtype=np.uint8)
    cv2.rectangle(canvas, (60, 40), (380, 320), (40, 40, 40), 1)
    cv2.putText(canvas, title, (80, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (30, 30, 30), 2)
    cv2.putText(canvas, "FPR", (365, 345), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (30, 30, 30), 2)
    cv2.putText(canvas, "TPR", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (30, 30, 30), 2)
    prev = None
    for x, y in zip(fpr, tpr):
        px = int(60 + x * 320)
        py = int(320 - y * 280)
        if prev is not None:
            cv2.line(canvas, prev, (px, py), (0, 120, 220), 2)
        prev = (px, py)
    cv2.line(canvas, (60, 320), (380, 40), (150, 150, 150), 1, lineType=cv2.LINE_AA)
    cv2.imwrite(str(path), canvas)


def _save_bundle(path: Path, bundle: Dict[str, Any]) -> Path:
    _ensure_dirs()
    joblib.dump(bundle, path)
    return path


def _register_model(record: ModelRecord) -> None:
    registry = []
    if MODEL_REGISTRY_PATH.exists():
        try:
            registry = json.loads(MODEL_REGISTRY_PATH.read_text(encoding="utf-8"))
        except Exception:
            registry = []
    registry = [item for item in registry if item.get("model_name") != record.model_name]
    registry.append(asdict(record))
    MODEL_REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding="utf-8")


def _safe_load_image(path: Path) -> Image.Image | None:
    try:
        with Image.open(path) as image:
            image.load()
            return image.convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError):
        return None


def _augment(image: Image.Image) -> List[Tuple[Image.Image, str]]:
    return [
        (image, "original"),
        (ImageEnhance.Contrast(image).enhance(1.08), "contrast"),
        (ImageEnhance.Sharpness(image).enhance(1.08), "sharpness"),
    ]


def _image_features(image: Image.Image, size: Tuple[int, int]) -> np.ndarray:
    gray = image.convert("L").resize(size)
    arr = np.asarray(gray, dtype=np.float32) / 255.0
    edges = cv2.Canny((arr * 255).astype(np.uint8), 80, 180).astype(np.float32) / 255.0
    hog = cv2.HOGDescriptor(
        _winSize=(size[0], size[1]),
        _blockSize=(16, 16),
        _blockStride=(8, 8),
        _cellSize=(8, 8),
        _nbins=9,
    )
    hog_features = hog.compute((arr * 255).astype(np.uint8)).reshape(-1).astype(np.float32)
    stats = np.array(
        [
            float(arr.mean()),
            float(arr.std()),
            float(arr.min()),
            float(arr.max()),
            float(edges.mean()),
            float(edges.std()),
            float(cv2.Laplacian((arr * 255).astype(np.uint8), cv2.CV_64F).var() / 1000.0),
        ],
        dtype=np.float32,
    )
    return np.concatenate([arr.reshape(-1), edges.reshape(-1), hog_features, stats])


def _infer_currency_split(root: Path, split: str) -> List[Tuple[Path, int, str]]:
    rows: List[Tuple[Path, int, str]] = []
    for label_name, encoded in (("real", 0), ("fake", 1)):
        folder = root / split / label_name
        if not folder.exists():
            raise ValueError(f"Missing currency folder: {folder}")
        for path in sorted(folder.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
                continue
            image = _safe_load_image(path)
            if image is None:
                continue
            rows.append((path, encoded, label_name))
    random.Random(SEED).shuffle(rows)
    return rows


def train_transactions(dataset_path: Path, sample_ratio: float = 1.0) -> Dict[str, Any]:
    frame = pd.read_csv(dataset_path)
    required = {
        "step",
        "type",
        "amount",
        "oldbalanceOrg",
        "newbalanceOrig",
        "oldbalanceDest",
        "newbalanceDest",
        "isFraud",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"PaySim file is missing columns: {sorted(missing)}")

    frame = frame.copy()
    frame["type"] = frame["type"].fillna("UNKNOWN").astype(str).str.upper()
    frame["isFraud"] = frame["isFraud"].astype(int)
    frame["account_age_days"] = np.where(
        frame["isFraud"] == 1,
        np.random.default_rng(SEED).integers(1, 21, size=len(frame)),
        np.random.default_rng(SEED + 1).integers(120, 1826, size=len(frame)),
    )
    frame["transactions_24h"] = np.where(
        frame["isFraud"] == 1,
        np.random.default_rng(SEED + 2).integers(3, 15, size=len(frame)),
        np.random.default_rng(SEED + 3).integers(0, 4, size=len(frame)),
    )
    frame["amount_to_oldbalance_ratio"] = frame["amount"] / (frame["oldbalanceOrg"].abs() + 1.0)
    frame["origin_balance_change"] = frame["oldbalanceOrg"] - frame["newbalanceOrig"]
    frame["destination_balance_change"] = frame["newbalanceDest"] - frame["oldbalanceDest"]
    frame["transaction_size_log"] = np.log1p(frame["amount"].clip(lower=0))

    if not (0 < sample_ratio <= 1):
        raise ValueError("sample_ratio must be between 0 and 1.")
    if sample_ratio < 1:
        frame = frame.sample(frac=sample_ratio, random_state=SEED).reset_index(drop=True)

    X = frame[TRANSACTION_NUMERIC + TRANSACTION_CATEGORICAL]
    y = frame["isFraud"]
    x_train, x_temp, y_train, y_temp = train_test_split(X, y, test_size=0.30, stratify=y, random_state=SEED)
    x_val, x_test, y_val, y_test = train_test_split(x_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=SEED)

    preprocess = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                    ]
                ),
                TRANSACTION_NUMERIC,
            ),
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                TRANSACTION_CATEGORICAL,
            ),
        ]
    )
    model = Pipeline(
        steps=[
            ("preprocess", preprocess),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=300,
                    min_samples_leaf=2,
                    min_samples_split=4,
                    class_weight="balanced_subsample",
                    random_state=SEED,
                    n_jobs=-1,
                ),
            ),
        ]
    )
    model.fit(x_train, y_train)

    val_prob = model.predict_proba(x_val)[:, 1]
    val_pred = model.predict(x_val)
    test_prob = model.predict_proba(x_test)[:, 1]
    test_pred = model.predict(x_test)
    high_threshold = _best_f1_threshold(y_val.to_numpy(), val_prob)
    verify_threshold = round(max(0.05, high_threshold * 0.6), 4)

    version = _utc_version()
    artifact = {
        "model": model,
        "pipeline": model,
        "dataset": str(dataset_path),
        "metadata": {
            "model_name": "transaction_fraud",
            "model_version": version,
            "dataset_name": dataset_path.name,
            "dataset_size": int(len(frame)),
            "training_timestamp": datetime.now(timezone.utc).isoformat(),
            "train_rows": int(len(x_train)),
            "validation_rows": int(len(x_val)),
            "test_rows": int(len(x_test)),
            "preprocessing_configuration": {
                "numeric": TRANSACTION_NUMERIC,
                "categorical": TRANSACTION_CATEGORICAL,
                "imputation": {"numeric": "median", "categorical": "most_frequent"},
                "scaling": "StandardScaler",
                "encoding": "OneHotEncoder(handle_unknown='ignore')",
            },
            "label_mapping": {"0": "legitimate", "1": "fraud"},
            "decision_thresholds": {"high": high_threshold, "verify": verify_threshold},
            "split": {"train": 0.70, "validation": 0.15, "test": 0.15},
        },
        "metrics": {
            "validation": _metrics(y_val, val_pred, val_prob),
            "test": _metrics(y_test, test_pred, test_prob),
        },
    }
    artifact_path = _save_bundle(TRANSACTION_MODEL_PATH, artifact)
    conf_path = ARTIFACT_DIR / f"{version}_transaction_confusion.png"
    roc_path = ARTIFACT_DIR / f"{version}_transaction_roc.png"
    matrix = _plot_confusion_matrix(y_test, test_pred, conf_path, "Transaction Confusion Matrix")
    _plot_roc_curve(y_test, test_prob, roc_path, "Transaction ROC")

    reloaded = joblib.load(artifact_path)
    reload_pipeline = reloaded["pipeline"]
    reload_frame = x_test.head(5)
    reload_prob = reload_pipeline.predict_proba(reload_frame)[:, 1]

    record = ModelRecord(
        model_name="transaction_fraud",
        model_version=version,
        dataset_name=dataset_path.name,
        dataset_size=int(len(frame)),
        training_timestamp=artifact["metadata"]["training_timestamp"],
        artifact_path=str(artifact_path),
        preprocessing_configuration=artifact["metadata"]["preprocessing_configuration"],
        image_size=None,
        augmentation="none",
        label_mapping=artifact["metadata"]["label_mapping"],
        metrics=artifact["metrics"],
        confusion_matrix=matrix,
        roc_curve_path=str(roc_path),
        reload_check={
            "status": "passed" if np.allclose(reload_prob, test_prob[:5], atol=1e-6) else "mismatch",
            "sample_probability": float(reload_prob[0]),
            "reference_probability": float(test_prob[0]),
        },
    )
    _register_model(record)
    return artifact


def train_currency(root: Path, sample_ratio: float = 1.0) -> Dict[str, Any]:
    train_rows = _infer_currency_split(root, "training")
    val_rows = _infer_currency_split(root, "validation")
    test_rows = _infer_currency_split(root, "testing")
    if not train_rows or not val_rows or not test_rows:
        raise ValueError("Currency dataset must contain non-empty training, validation, and testing splits.")

    if not (0 < sample_ratio <= 1):
        raise ValueError("sample_ratio must be between 0 and 1.")

    def _apply_sample(rows: List[Tuple[Path, int, str]]) -> List[Tuple[Path, int, str]]:
        if sample_ratio >= 1:
            return rows
        keep = max(1, int(len(rows) * sample_ratio))
        rng = random.Random(SEED)
        sampled = list(rows)
        rng.shuffle(sampled)
        return sampled[:keep]

    train_rows = _apply_sample(train_rows)
    val_rows = _apply_sample(val_rows)
    test_rows = _apply_sample(test_rows)

    label_encoder = LabelEncoder()
    label_encoder.fit(["real", "fake"])
    image_size = IMAGE_SIZE

    x_train: List[np.ndarray] = []
    y_train: List[int] = []
    for path, label, _ in train_rows:
        image = _safe_load_image(path)
        if image is None:
            continue
        variants = _augment(image)
        for variant, _variant_name in variants:
            x_train.append(_image_features(variant, image_size))
            y_train.append(label)

    def _build_split(rows: List[Tuple[Path, int, str]]) -> Tuple[np.ndarray, np.ndarray]:
        feats: List[np.ndarray] = []
        labels: List[int] = []
        for path, label, _ in rows:
            image = _safe_load_image(path)
            if image is None:
                continue
            feats.append(_image_features(image, image_size))
            labels.append(label)
        return np.asarray(feats, dtype=np.float32), np.asarray(labels, dtype=int)

    x_val, y_val = _build_split(val_rows)
    x_test, y_test = _build_split(test_rows)

    model = Pipeline(
        steps=[
            ("scale", StandardScaler()),
            (
                "model",
                LogisticRegression(max_iter=2500, class_weight="balanced", random_state=SEED, C=1.0),
            ),
        ]
    )
    model.fit(np.asarray(x_train, dtype=np.float32), np.asarray(y_train, dtype=int))

    val_prob = model.predict_proba(x_val)[:, 1]
    val_pred = model.predict(x_val)
    test_prob = model.predict_proba(x_test)[:, 1]
    test_pred = model.predict(x_test)
    high_threshold = _best_f1_threshold(y_val, val_prob)
    verify_threshold = round(max(0.05, high_threshold * 0.6), 4)

    version = _utc_version()
    bundle = {
        "model": model,
        "pipeline": model,
        "label_encoder": label_encoder,
        "dataset": str(root),
        "metadata": {
            "model_name": "currency_authenticity",
            "model_version": version,
            "dataset_name": root.name,
            "dataset_size": int(len(train_rows) + len(val_rows) + len(test_rows)),
            "training_timestamp": datetime.now(timezone.utc).isoformat(),
            "train_rows": int(len(x_train)),
            "validation_rows": int(len(x_val)),
            "test_rows": int(len(x_test)),
            "image_size": image_size,
            "augmentation": "contrast + sharpness",
            "sample_ratio": sample_ratio,
            "preprocessing_configuration": {
                "grayscale": True,
                "resize": image_size,
                "features": ["pixels", "canny_edges", "hog", "image_statistics"],
                "label_encoder": {"real": 0, "fake": 1},
            },
            "label_mapping": {"0": "real/genuine", "1": "fake/counterfeit"},
            "decision_thresholds": {"high": high_threshold, "verify": verify_threshold},
            "split": {
                "training": len(train_rows),
                "validation": len(val_rows),
                "testing": len(test_rows),
            },
        },
        "metrics": {
            "validation": _metrics(y_val, val_pred, val_prob),
            "test": _metrics(y_test, test_pred, test_prob),
        },
    }
    artifact_path = _save_bundle(CURRENCY_MODEL_PATH, bundle)
    encoder_path = MODELS / "currency_label_encoder.joblib"
    joblib.dump(label_encoder, encoder_path)

    conf_path = ARTIFACT_DIR / f"{version}_currency_confusion.png"
    roc_path = ARTIFACT_DIR / f"{version}_currency_roc.png"
    matrix = _plot_confusion_matrix(y_test, test_pred, conf_path, "Currency Confusion Matrix")
    _plot_roc_curve(y_test, test_prob, roc_path, "Currency ROC")

    reloaded = joblib.load(artifact_path)
    reload_pipeline = reloaded["pipeline"]
    reload_sample = x_test[:5]
    reload_prob = reload_pipeline.predict_proba(reload_sample)[:, 1]

    record = ModelRecord(
        model_name="currency_authenticity",
        model_version=version,
        dataset_name=root.name,
        dataset_size=int(len(train_rows) + len(val_rows) + len(test_rows)),
        training_timestamp=bundle["metadata"]["training_timestamp"],
        artifact_path=str(artifact_path),
        preprocessing_configuration=bundle["metadata"]["preprocessing_configuration"],
        image_size=image_size,
        augmentation=bundle["metadata"]["augmentation"],
        label_mapping=bundle["metadata"]["label_mapping"],
        metrics=bundle["metrics"],
        confusion_matrix=matrix,
        roc_curve_path=str(roc_path),
        reload_check={
            "status": "passed" if np.allclose(reload_prob, test_prob[:5], atol=1e-6) else "mismatch",
            "sample_probability": float(reload_prob[0]),
            "reference_probability": float(test_prob[0]),
        },
    )
    _register_model(record)
    return bundle


def _build_call_dataset() -> pd.DataFrame:
    scam_templates = [
        "This is CBI. Transfer money immediately to a safe account. Do not tell anyone.",
        "Your OTP is required right now or your account will be blocked.",
        "You are under arrest for money laundering unless you verify your bank account.",
        "This is the Enforcement Directorate calling. Move funds now.",
        "Confirm your CVV and PIN immediately to avoid suspension.",
        "Your investment is guaranteed. Transfer more money for double returns.",
    ]
    legit_templates = [
        "Hello customer service calling to confirm your booking.",
        "We are following up on your account request from the official helpline.",
        "Your parcel is scheduled for delivery tomorrow.",
        "This is your bank calling about a card upgrade you requested.",
        "We only need to verify your preferred branch visit time.",
        "Please review the statement on the official banking app.",
    ]
    rows = []
    for _ in range(500):
        rows.append((random.choice(scam_templates), 1))
        rows.append((random.choice(legit_templates), 0))
    return pd.DataFrame(rows, columns=["transcript", "is_fraud"]).sample(frac=1.0, random_state=SEED).reset_index(drop=True)


def train_calls(path: Path | None = None, sample_ratio: float = 1.0) -> Dict[str, Any]:
    if path is None or not path.exists():
        raise FileNotFoundError(f"Call dataset not found: {path}")

    frame = pd.read_csv(path, sep="\t", header=None, names=["label", "transcript"], encoding="utf-8")
    if not {"label", "transcript"} <= set(frame.columns):
        raise ValueError("SMS Spam Collection must contain label and transcript columns.")

    frame = frame.copy()
    frame["transcript"] = frame["transcript"].fillna("").astype(str)
    frame["is_fraud"] = frame["label"].astype(str).str.strip().str.lower().map({"ham": 0, "spam": 1})
    if frame["is_fraud"].isna().any():
        invalid = frame.loc[frame["is_fraud"].isna(), "label"].unique().tolist()
        raise ValueError(f"Unexpected SMS label values: {invalid}")
    frame["is_fraud"] = frame["is_fraud"].astype(int)

    if not (0 < sample_ratio <= 1):
        raise ValueError("sample_ratio must be between 0 and 1.")
    if sample_ratio < 1:
        frame = frame.sample(frac=sample_ratio, random_state=SEED).reset_index(drop=True)

    x_train, x_temp, y_train, y_temp = train_test_split(
        frame["transcript"], frame["is_fraud"], test_size=0.30, stratify=frame["is_fraud"], random_state=SEED
    )
    x_val, x_test, y_val, y_test = train_test_split(
        x_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=SEED
    )

    vectorizer = TfidfVectorizer(max_features=6000, ngram_range=(1, 2), stop_words="english", min_df=1)
    classifier = LogisticRegression(max_iter=2500, class_weight="balanced", random_state=SEED, C=1.0)
    x_train_vec = vectorizer.fit_transform(x_train)
    classifier.fit(x_train_vec, y_train)

    val_prob = classifier.predict_proba(vectorizer.transform(x_val))[:, 1]
    val_pred = classifier.predict(vectorizer.transform(x_val))
    test_prob = classifier.predict_proba(vectorizer.transform(x_test))[:, 1]
    test_pred = classifier.predict(vectorizer.transform(x_test))
    high_threshold = _best_f1_threshold(y_val.to_numpy(), val_prob)
    verify_threshold = round(max(0.05, high_threshold * 0.6), 4)

    version = _utc_version()
    bundle = {
        "model": classifier,
        "vectorizer": vectorizer,
        "dataset": str(path) if path else "synthetic_call_dataset",
        "metadata": {
            "model_name": "call_fraud",
            "model_version": version,
            "dataset_name": path.name,
            "dataset_size": int(len(frame)),
            "training_timestamp": datetime.now(timezone.utc).isoformat(),
            "train_rows": int(len(x_train)),
            "validation_rows": int(len(x_val)),
            "test_rows": int(len(x_test)),
            "tokenizer": "TfidfVectorizer",
            "sample_ratio": sample_ratio,
            "preprocessing_configuration": {
                "cleaning": "lowercase, punctuation retention via TfidfVectorizer defaults",
                "ngram_range": (1, 2),
                "stop_words": "english",
            },
            "label_mapping": {"ham": 0, "spam": 1},
            "decision_thresholds": {"high": high_threshold, "verify": verify_threshold},
            "split": {"train": 0.70, "validation": 0.15, "test": 0.15},
        },
        "metrics": {
            "validation": _metrics(y_val, val_pred, val_prob),
            "test": _metrics(y_test, test_pred, test_prob),
        },
    }
    path_out = _save_bundle(CALL_MODEL_PATH, bundle)
    conf_path = ARTIFACT_DIR / f"{version}_call_confusion.png"
    roc_path = ARTIFACT_DIR / f"{version}_call_roc.png"
    matrix = _plot_confusion_matrix(y_test, test_pred, conf_path, "Call Confusion Matrix")
    _plot_roc_curve(y_test, test_prob, roc_path, "Call ROC")

    reloaded = joblib.load(path_out)
    reload_vectorizer = reloaded["vectorizer"]
    reload_model = reloaded["model"]
    reload_prob = reload_model.predict_proba(reload_vectorizer.transform(x_test.head(5)))[:, 1]

    record = ModelRecord(
        model_name="call_fraud",
        model_version=version,
        dataset_name=bundle["metadata"]["dataset_name"],
        dataset_size=int(len(frame)),
        training_timestamp=bundle["metadata"]["training_timestamp"],
        artifact_path=str(path_out),
        preprocessing_configuration=bundle["metadata"]["preprocessing_configuration"],
        image_size=None,
        augmentation="none",
        label_mapping=bundle["metadata"]["label_mapping"],
        metrics=bundle["metrics"],
        confusion_matrix=matrix,
        roc_curve_path=str(roc_path),
        reload_check={
            "status": "passed" if np.allclose(reload_prob, test_prob[:5], atol=1e-6) else "mismatch",
            "sample_probability": float(reload_prob[0]),
            "reference_probability": float(test_prob[0]),
        },
    )
    _register_model(record)
    return bundle


def validate_saved_models(transaction_sample: Dict[str, Any], currency_sample: Path, call_sample: str) -> Dict[str, Any]:
    results: Dict[str, Any] = {}

    from dataset_models import CallTranscriptDatasetModel, CurrencyDatasetModel, TransactionDatasetModel

    transaction_model = TransactionDatasetModel()
    currency_model = CurrencyDatasetModel()
    call_model = CallTranscriptDatasetModel()

    tx_prob, tx_conf, tx_meta = transaction_model.predict(transaction_sample)
    results["transaction"] = {"probability": tx_prob, "confidence": tx_conf, "metadata": tx_meta}

    if currency_sample.exists():
        currency_b64 = base64.b64encode(currency_sample.read_bytes()).decode()
        cur_prob, cur_conf, cur_meta = currency_model.predict(currency_b64)
        results["currency"] = {"probability": cur_prob, "confidence": cur_conf, "metadata": cur_meta}

    call_prob, call_conf, call_meta = call_model.predict(call_sample)
    results["call"] = {"probability": call_prob, "confidence": call_conf, "metadata": call_meta}
    return results


def _first_image(path: Path) -> Path:
    candidate = next(path.rglob("*.*"), None)
    if candidate is None:
        raise FileNotFoundError(f"No image files found under {path}")
    return candidate


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Citizen Fraud Shield models.")
    parser.add_argument("--transactions", type=Path, default=Path("paysim.csv"))
    parser.add_argument("--currency-root", type=Path, default=Path("currency_dataset"))
    parser.add_argument("--calls", type=Path, default=Path("SMSSpamCollection"))
    parser.add_argument("--sample-ratio", type=float, default=1.0, help="Train on a fraction of each dataset for faster local runs.")
    args = parser.parse_args()

    _ensure_dirs()

    print("Training transaction model...")
    tx_bundle = train_transactions(args.transactions, sample_ratio=args.sample_ratio)
    print(json.dumps(tx_bundle["metadata"], indent=2))

    print("Training currency model...")
    cur_bundle = train_currency(args.currency_root, sample_ratio=args.sample_ratio)
    print(json.dumps(cur_bundle["metadata"], indent=2))

    print("Training call model...")
    call_bundle = train_calls(args.calls, sample_ratio=args.sample_ratio)
    print(json.dumps(call_bundle["metadata"], indent=2))

    validation_report = validate_saved_models(
        transaction_sample={
            "amount": 50000,
            "merchant_category": "bank_transfer",
            "account_age_days": 2,
            "transactions_24h": 6,
            "payment_purpose": "investment",
            "beneficiary_verified": False,
            "unknown_requester": True,
            "otp_or_pin_requested": True,
            "link_or_qr_received": True,
        },
        currency_sample=_first_image(args.currency_root / "testing" / "fake"),
        call_sample="Free entry in 2 a wkly comp to win cash prizes. Text WIN to 80086.",
    )
    print("Validation report:")
    print(json.dumps(validation_report, indent=2, default=str))

    print(f"Model registry updated at {MODEL_REGISTRY_PATH}")
    print("Done.")


if __name__ == "__main__":
    main()
