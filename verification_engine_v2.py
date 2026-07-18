"""Dataset-backed verification engine for Citizen Fraud Shield."""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

from dataset_models import CallTranscriptDatasetModel, CurrencyDatasetModel, TransactionDatasetModel


class RiskLevel(Enum):
    VERIFY = "VERIFY"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class VerificationResult:
    timestamp: str
    input_type: str
    trust_score: float
    fraud_probability: float
    risk_level: RiskLevel
    action: str
    recommendation: str
    detailed_factors: Dict[str, Any]
    alert_id: str
    explanation: str
    confidence: float


class EnhancedVerificationEngineV3:
    """Live verification engine that only uses trained dataset-backed models."""

    def __init__(self, db_path: str = "fraud_alerts.db"):
        self.db_path = db_path
        self.call_model = CallTranscriptDatasetModel()
        self.currency_model = CurrencyDatasetModel()
        self.transaction_model = TransactionDatasetModel()
        self._init_database()

    def _init_database(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS fraud_alerts (
                alert_id TEXT PRIMARY KEY,
                timestamp TEXT,
                input_type TEXT,
                trust_score REAL,
                fraud_probability REAL,
                risk_level TEXT,
                action TEXT,
                recommendation TEXT,
                detailed_factors TEXT,
                explanation TEXT,
                confidence REAL
            )
            """
        )
        conn.commit()
        conn.close()

    def verify(self, input_type: str, data: Dict[str, Any]) -> VerificationResult:
        timestamp = datetime.now().isoformat()
        alert_id = f"{input_type}_{int(datetime.now().timestamp() * 1000)}"

        if input_type == "call":
            transcript = data.get("transcript", "")
            if not str(transcript).strip():
                fraud_prob, confidence, factors = 0.5, 0.0, {
                    "model_status": "verify",
                    "reason": "No transcript was provided, so the call must be manually reviewed.",
                }
                explanation = factors["reason"]
                return self._finalize(timestamp, alert_id, input_type, fraud_prob, confidence, factors, explanation)
            fraud_prob, confidence, factors = self.call_model.predict(transcript)
            explanation = (
                "Fraud probability was produced by the labelled transcript model."
                if confidence > 0
                else factors.get("reason", "Call cannot be rated safely until a labelled transcript model is trained.")
            )
        elif input_type == "call_recording":
            transcript = data.get("transcript", "")
            if not str(transcript).strip():
                fraud_prob, confidence, factors = 0.5, 0.0, {
                    "model_status": "verify",
                    "reason": "No transcript was available from the audio input, so manual review is required.",
                }
                explanation = factors["reason"]
                return self._finalize(timestamp, alert_id, input_type, fraud_prob, confidence, factors, explanation)
            fraud_prob, confidence, factors = self.call_model.predict(transcript)
            explanation = (
                "Fraud probability was produced by the labelled transcript model."
                if confidence > 0
                else factors.get("reason", "Call recording cannot be rated safely until a labelled transcript model is trained.")
            )
        elif input_type == "currency":
            image = data.get("image_base64")
            if not image:
                fraud_prob, confidence, factors = 0.5, 0.0, {
                    "model_status": "verify",
                    "reason": "A currency image is required.",
                }
            else:
                fraud_prob, confidence, factors = self.currency_model.predict(image)
            explanation = (
                "Counterfeit probability was produced by the labelled-image model."
                if confidence > 0
                else factors.get("reason", "Currency cannot be authenticated until a labelled model is trained or a valid image is supplied.")
            )
        elif input_type == "transaction":
            transaction_data = data.get("transaction", {})
            fraud_prob, confidence, factors = self.transaction_model.predict(transaction_data)
            explanation = (
                "Fraud probability was produced by the labelled transaction model."
                if confidence > 0
                else factors.get("reason", "Transaction cannot be rated safely until a labelled transaction model is trained.")
            )
        else:
            raise ValueError(f"Unknown input_type: {input_type}")

        return self._finalize(timestamp, alert_id, input_type, fraud_prob, confidence, factors, explanation)

    def _finalize(
        self,
        timestamp: str,
        alert_id: str,
        input_type: str,
        fraud_prob: float,
        confidence: float,
        factors: Dict[str, Any],
        explanation: str,
    ) -> VerificationResult:
        thresholds = factors.get("training_metadata", {}).get("decision_thresholds", {})
        high_threshold = float(thresholds.get("high", 0.5))
        verify_threshold = float(thresholds.get("verify", max(0.05, high_threshold * 0.6)))
        if confidence <= 0:
            action = "VERIFY"
            risk_level = RiskLevel.VERIFY
            fraud_prob = 0.5
            trust_score = 0.0
        elif fraud_prob >= high_threshold:
            action = "BLOCK"
            risk_level = RiskLevel.HIGH
            trust_score = max(0.0, (1 - fraud_prob) * confidence * 100)
        elif fraud_prob >= verify_threshold:
            action = "VERIFY"
            risk_level = RiskLevel.MEDIUM
            trust_score = max(0.0, (1 - fraud_prob) * confidence * 100)
        else:
            action = "ALLOW"
            risk_level = RiskLevel.LOW
            trust_score = max(0.0, (1 - fraud_prob) * confidence * 100)

        recommendation = self._get_recommendation(action, input_type)
        result = VerificationResult(
            timestamp=timestamp,
            input_type=input_type,
            trust_score=trust_score,
            fraud_probability=fraud_prob,
            risk_level=risk_level,
            action=action,
            recommendation=recommendation,
            detailed_factors=factors,
            alert_id=alert_id,
            explanation=explanation,
            confidence=confidence,
        )

        if risk_level in {RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.VERIFY}:
            self._log_alert(result)

        return result

    def _get_recommendation(self, action: str, input_type: str) -> str:
        recommendations = {
            ("BLOCK", "call"): "DANGER: treat this as a scam call. Hang up and verify independently.",
            ("BLOCK", "call_recording"): "DANGER: treat this as a scam recording. Save evidence and report it.",
            ("BLOCK", "currency"): "WARNING: counterfeit risk is high. Do not use the note.",
            ("BLOCK", "transaction"): "ALERT: fraud risk is high. Do not proceed and verify with your bank.",
            ("VERIFY", "call"): "Verify the caller independently before sharing any sensitive information.",
            ("VERIFY", "call_recording"): "Verify the recording context independently before acting.",
            ("VERIFY", "currency"): "Check the note manually with security features or a bank if unsure.",
            ("VERIFY", "transaction"): "Verify beneficiary, amount, and request source independently.",
            ("ALLOW", "call"): "The call currently appears lower risk, but remain cautious.",
            ("ALLOW", "currency"): "The note currently appears lower risk, but remain cautious.",
            ("ALLOW", "transaction"): "The transaction currently appears lower risk, but remain cautious.",
        }
        return recommendations.get((action, input_type), "Review required.")

    def _log_alert(self, result: VerificationResult) -> None:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO fraud_alerts
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.alert_id,
                    result.timestamp,
                    result.input_type,
                    result.trust_score,
                    result.fraud_probability,
                    result.risk_level.value,
                    result.action,
                    result.recommendation,
                    json.dumps(result.detailed_factors),
                    result.explanation,
                    result.confidence,
                ),
            )
            conn.commit()
            conn.close()
        except Exception as exc:
            print(f"Database logging error: {exc}")

    def get_recent_alerts(self, limit: int = 20, risk_level: str | None = None) -> List[Dict[str, Any]]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            if risk_level:
                cursor.execute(
                    "SELECT timestamp, input_type, risk_level FROM fraud_alerts WHERE risk_level = ? ORDER BY timestamp DESC LIMIT ?",
                    (risk_level, limit),
                )
            else:
                cursor.execute(
                    "SELECT timestamp, input_type, risk_level FROM fraud_alerts ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                )
            rows = cursor.fetchall()
            conn.close()
            return [{"timestamp": row[0], "type": row[1], "risk": row[2]} for row in rows]
        except Exception:
            return []

    def get_statistics(self, hours: int = 24) -> Dict[str, Any]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cutoff = datetime.now().isoformat()
            cursor.execute(
                "SELECT risk_level, COUNT(*) FROM fraud_alerts WHERE timestamp <= ? GROUP BY risk_level",
                (cutoff,),
            )
            stats = dict(cursor.fetchall())
            conn.close()
            return {
                "total_alerts": sum(stats.values()),
                "high_risk": stats.get("HIGH", 0),
                "medium_risk": stats.get("MEDIUM", 0),
                "low_risk": stats.get("LOW", 0),
                "verify": stats.get("VERIFY", 0),
            }
        except Exception as exc:
            return {"error": str(exc)}


def result_to_dict(result: VerificationResult) -> Dict[str, Any]:
    detailed = result.detailed_factors or {}
    return {
        "alert_id": result.alert_id,
        "timestamp": result.timestamp,
        "input_type": result.input_type,
        "trust_score": round(result.trust_score, 2),
        "fraud_probability": round(result.fraud_probability, 3),
        "risk_level": result.risk_level.value,
        "action": result.action,
        "status": "VERIFY" if result.risk_level == RiskLevel.VERIFY else "FINAL",
        "confidence": round(result.confidence, 3),
        "model_version": detailed.get("model_version"),
        "evaluation_metrics": detailed.get("evaluation_metrics", {}),
        "recommendation": result.recommendation,
        "explanation": result.explanation,
        "detailed_factors": detailed,
    }
