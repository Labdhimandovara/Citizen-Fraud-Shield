"""
risk_scoring_engine.py
Shared scoring engine for Citizen Fraud Shield v4
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple


class RiskLevel(str, Enum):
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class ScoreResult:
    evidence_score: float
    fraud_probability: float
    trust_score: float
    confidence: float
    risk_level: RiskLevel
    reasons: List[str]


class RiskScoringEngine:
    def __init__(self):
        self.positive_weights = {
            "verified_beneficiary": 15,
            "known_device": 10,
            "known_location": 10,
            "old_account": 15,
            "trusted_merchant": 10,
        }

    def score(self, evidence: List[Tuple[str, float]],
              positives: List[str] | None = None,
              input_quality: float = 90) -> ScoreResult:

        positives = positives or []

        evidence_score = min(100.0, sum(v for _, v in evidence))

        # Non-linear fraud probability
        if evidence_score <= 10:
            fraud = 2 + evidence_score * 0.6
        elif evidence_score <= 30:
            fraud = 8 + (evidence_score - 10) * 1.1
        elif evidence_score <= 60:
            fraud = 30 + (evidence_score - 30) * 1.2
        elif evidence_score <= 80:
            fraud = 66 + (evidence_score - 60) * 1.2
        else:
            fraud = 90 + (evidence_score - 80) * 0.45

        fraud = round(min(99.0, fraud), 1)

        positive = sum(self.positive_weights.get(x, 0) for x in positives)
        trust = max(1, min(99, round(100 - evidence_score + positive * 0.5)))

        confidence = min(
            99,
            round(
                45
                + min(30, len(evidence) * 6)
                + min(15, evidence_score / 10)
                + (input_quality / 10),
                1,
            ),
        )

        if fraud < 15:
            level = RiskLevel.SAFE
        elif fraud < 35:
            level = RiskLevel.LOW
        elif fraud < 60:
            level = RiskLevel.MEDIUM
        elif fraud < 85:
            level = RiskLevel.HIGH
        else:
            level = RiskLevel.CRITICAL

        return ScoreResult(
            evidence_score=round(evidence_score, 1),
            fraud_probability=fraud,
            trust_score=trust,
            confidence=confidence,
            risk_level=level,
            reasons=[x for x, _ in evidence],
        )
