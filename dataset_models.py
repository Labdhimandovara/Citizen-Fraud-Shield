"""Dataset-backed model loaders and feature extraction helpers."""
from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import joblib
import numpy as np
import pandas as pd
import cv2
from PIL import Image

ROOT = Path(__file__).parent
MODELS = ROOT / "models"


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

CALL_MODEL_PATH = MODELS / "call_fraud.joblib"
TRANSACTION_MODEL_PATH = MODELS / "transaction_fraud.joblib"
CURRENCY_MODEL_PATH = MODELS / "currency_authenticity.joblib"


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _normalize_transaction_type(transaction: Dict[str, Any]) -> str:
    raw = (
        transaction.get("type")
        or transaction.get("merchant_category")
        or transaction.get("payment_purpose")
        or transaction.get("payment_channel")
        or "UNKNOWN"
    )
    value = str(raw).strip().upper().replace(" ", "_").replace("-", "_")

    aliases = {
        "ONLINE_SHOPPING": "PAYMENT",
        "FOOD_DELIVERY": "PAYMENT",
        "TRAVEL": "PAYMENT",
        "UTILITIES": "PAYMENT",
        "PURCHASE": "PAYMENT",
        "BILL": "PAYMENT",
        "REFUND": "CASH_IN",
        "FAMILY": "TRANSFER",
        "FRIEND_OR_FAMILY": "TRANSFER",
        "BANK_TRANSFER": "TRANSFER",
        "INVESTMENT": "TRANSFER",
        "UPI": "PAYMENT",
        "CARD": "PAYMENT",
        "WALLET": "PAYMENT",
        "CASH": "CASH_IN",
    }
    return aliases.get(value, value)


def transaction_row(transaction: Dict[str, Any]) -> Dict[str, Any]:
    row = {field: _safe_float(transaction.get(field), 0.0) for field in TRANSACTION_NUMERIC}
    row["type"] = _normalize_transaction_type(transaction)
    row["account_age_days"] = _safe_float(transaction.get("account_age_days"), 365.0)
    row["transactions_24h"] = _safe_float(transaction.get("transactions_24h"), 0.0)
    row["amount_to_oldbalance_ratio"] = row["amount"] / (abs(row["oldbalanceOrg"]) + 1.0)
    row["origin_balance_change"] = row["oldbalanceOrg"] - row["newbalanceOrig"]
    row["destination_balance_change"] = row["newbalanceDest"] - row["oldbalanceDest"]
    row["transaction_size_log"] = float(np.log1p(max(row["amount"], 0.0)))
    return row


def _image_feature_vector(image: Image.Image, size: Tuple[int, int]) -> np.ndarray:
    resized = image.convert("L").resize(size)
    arr = np.asarray(resized, dtype=np.float32) / 255.0
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


def image_to_vector(image_base64: str, size: Tuple[int, int] = (96, 96)) -> np.ndarray:
    raw = base64.b64decode(image_base64.split(",")[-1], validate=False)
    image = Image.open(io.BytesIO(raw))
    return _image_feature_vector(image, size).reshape(1, -1)


def file_to_vector(path: Path, size: Tuple[int, int] = (96, 96)) -> np.ndarray:
    with path.open("rb") as handle:
        raw = handle.read()
    image = Image.open(io.BytesIO(raw))
    return _image_feature_vector(image, size).reshape(1, -1)


class LoadedBundle:
    def __init__(self, bundle: Dict[str, Any] | None):
        self.bundle = bundle or {}

    @property
    def model(self):
        return self.bundle.get("model")

    @property
    def pipeline(self):
        return self.bundle.get("pipeline")

    @property
    def vectorizer(self):
        return self.bundle.get("vectorizer")

    @property
    def metadata(self):
        return self.bundle.get("metadata", {})

    @property
    def metrics(self):
        return self.bundle.get("metrics", {})

    @property
    def dataset(self):
        return self.bundle.get("dataset")

    @property
    def decision_thresholds(self):
        return self.metadata.get("decision_thresholds", {})

    def loaded(self) -> bool:
        return bool(self.model or self.pipeline or self.vectorizer)


class TransactionDatasetModel:
    def __init__(self, model_path: Path = TRANSACTION_MODEL_PATH):
        self.path = model_path
        self.bundle = LoadedBundle(joblib.load(model_path) if model_path.exists() else None)

    def predict(self, transaction: Dict[str, Any]) -> Tuple[float, float, Dict[str, Any]]:
        if not self.bundle.loaded():
            return 0.5, 0.0, {
                "model_status": "not_trained",
                "reason": "transaction_fraud.joblib is missing or unreadable",
            }

        row = transaction_row(transaction)
        pipeline = self.bundle.pipeline
        model = self.bundle.model
        if pipeline is None or model is None:
            return 0.5, 0.0, {
                "model_status": "corrupted",
                "reason": "Transaction model bundle is missing pipeline or estimator",
            }

        try:
            frame = pd.DataFrame([row], columns=TRANSACTION_NUMERIC + TRANSACTION_CATEGORICAL)
            proba = float(pipeline.predict_proba(frame)[0, 1])
            return proba, self._confidence(), self._factor_payload("transaction", row)
        except Exception as exc:
            return 0.5, 0.0, {
                "model_status": "inference_failed",
                "reason": str(exc),
                "model_version": self.bundle.metadata.get("model_version"),
                "evaluation_metrics": self.bundle.metrics,
            }

    def _confidence(self) -> float:
        metric = (
            self.bundle.metrics.get("validation", {}).get("f1")
            or self.bundle.metrics.get("validation", {}).get("precision")
            or self.bundle.metrics.get("test", {}).get("f1")
            or self.bundle.metrics.get("test", {}).get("precision")
            or self.bundle.metadata.get("validation_precision")
            or 0.0
        )
        return float(metric)

    def _factor_payload(self, kind: str, row: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "model_status": "trained",
            "model_name": self.bundle.metadata.get("model_name", kind),
            "model_version": self.bundle.metadata.get("model_version", "v1"),
            "dataset": self.bundle.dataset,
            "training_metadata": self.bundle.metadata,
            "evaluation_metrics": self.bundle.metrics,
            "input_preview": row,
        }


class CurrencyDatasetModel:
    def __init__(self, model_path: Path = CURRENCY_MODEL_PATH):
        self.path = model_path
        self.bundle = LoadedBundle(joblib.load(model_path) if model_path.exists() else None)

    def predict(self, image_base64: str) -> Tuple[float, float, Dict[str, Any]]:
        if not self.bundle.loaded():
            return 0.5, 0.0, {
                "model_status": "not_trained",
                "reason": "currency_authenticity.joblib is missing or unreadable",
            }

        pipeline = self.bundle.pipeline
        if pipeline is None:
            return 0.5, 0.0, {
                "model_status": "corrupted",
                "reason": "Currency model bundle is missing pipeline or estimator",
            }

        try:
            vector = image_to_vector(image_base64, tuple(self.bundle.metadata.get("image_size", (96, 96))))
            proba = float(pipeline.predict_proba(vector)[0, 1])
            return proba, self._confidence(), self._factor_payload("currency")
        except Exception as exc:
            return 0.5, 0.0, {
                "model_status": "inference_failed",
                "reason": str(exc),
                "model_version": self.bundle.metadata.get("model_version"),
                "evaluation_metrics": self.bundle.metrics,
            }

    def _confidence(self) -> float:
        metric = (
            self.bundle.metrics.get("validation", {}).get("f1")
            or self.bundle.metrics.get("validation", {}).get("precision")
            or self.bundle.metrics.get("test", {}).get("f1")
            or self.bundle.metrics.get("test", {}).get("precision")
            or self.bundle.metadata.get("validation_precision")
            or 0.0
        )
        return float(metric)

    def _factor_payload(self, kind: str) -> Dict[str, Any]:
        return {
            "model_status": "trained",
            "model_name": self.bundle.metadata.get("model_name", kind),
            "model_version": self.bundle.metadata.get("model_version", "v1"),
            "dataset": self.bundle.dataset,
            "training_metadata": self.bundle.metadata,
            "evaluation_metrics": self.bundle.metrics,
        }


class CallTranscriptDatasetModel:
    def __init__(self, model_path: Path = CALL_MODEL_PATH):
        self.path = model_path
        self.bundle = LoadedBundle(joblib.load(model_path) if model_path.exists() else None)

    def predict(self, transcript: str) -> Tuple[float, float, Dict[str, Any]]:
        if not self.bundle.loaded():
            return 0.5, 0.0, {
                "model_status": "not_trained",
                "reason": "call_fraud.joblib is missing or unreadable",
            }

        if not str(transcript or "").strip():
            return 0.5, 0.0, {
                "model_status": "verify",
                "reason": "No transcript was provided, so manual review is required.",
            }

        pipeline = self.bundle.pipeline
        vectorizer = self.bundle.vectorizer
        model = self.bundle.model
        if model is None or vectorizer is None:
            return 0.5, 0.0, {
                "model_status": "corrupted",
                "reason": "Call model bundle is missing vectorizer or estimator",
            }

        try:
            cleaned = str(transcript or "")
            proba = float(model.predict_proba(vectorizer.transform([cleaned]))[0, 1])
            return proba, self._confidence(), self._factor_payload("call")
        except Exception as exc:
            return 0.5, 0.0, {
                "model_status": "inference_failed",
                "reason": str(exc),
                "model_version": self.bundle.metadata.get("model_version"),
                "evaluation_metrics": self.bundle.metrics,
            }

    def _confidence(self) -> float:
        metric = (
            self.bundle.metrics.get("validation", {}).get("f1")
            or self.bundle.metrics.get("validation", {}).get("precision")
            or self.bundle.metrics.get("test", {}).get("f1")
            or self.bundle.metrics.get("test", {}).get("precision")
            or self.bundle.metadata.get("validation_precision")
            or 0.0
        )
        return float(metric)

    def _factor_payload(self, kind: str) -> Dict[str, Any]:
        return {
            "model_status": "trained",
            "model_name": self.bundle.metadata.get("model_name", kind),
            "model_version": self.bundle.metadata.get("model_version", "v1"),
            "dataset": self.bundle.dataset,
            "training_metadata": self.bundle.metadata,
            "evaluation_metrics": self.bundle.metrics,
        }
