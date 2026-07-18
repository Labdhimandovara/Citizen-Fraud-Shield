from __future__ import annotations

import base64
from pathlib import Path

from dataset_models import CurrencyDatasetModel, TransactionDatasetModel
from verification_engine_v2 import EnhancedVerificationEngineV3


def test_empty_call_returns_verify():
    engine = EnhancedVerificationEngineV3()
    result = engine.verify("call", {"transcript": ""})
    assert result.risk_level.value == "VERIFY"
    assert result.confidence == 0.0
    assert result.action == "VERIFY"


def test_transaction_high_risk_smoke():
    engine = EnhancedVerificationEngineV3()
    result = engine.verify(
        "transaction",
        {
            "transaction": {
                "amount": 50000,
                "merchant_category": "bank_transfer",
                "account_age_days": 2,
                "transactions_24h": 6,
                "payment_purpose": "investment",
                "beneficiary_verified": False,
                "unknown_requester": True,
                "otp_or_pin_requested": True,
                "link_or_qr_received": True,
            }
        },
    )
    assert result.risk_level.value == "HIGH"
    assert result.fraud_probability >= 0.7


def test_currency_model_separates_real_and_fake():
    model = CurrencyDatasetModel()
    fake = Path(r"currency_dataset/testing/fake/aug_1388_WhatsApp Image 2025-04-05 at 10.59.15.jpeg")
    real = next(Path(r"currency_dataset/testing/real").rglob("*.*"))
    fake_prob, fake_conf, _ = model.predict(base64.b64encode(fake.read_bytes()).decode())
    real_prob, real_conf, _ = model.predict(base64.b64encode(real.read_bytes()).decode())
    assert fake_conf > 0
    assert real_conf > 0
    assert fake_prob > real_prob
    assert fake_prob >= 0.7
    assert real_prob <= 0.3


def test_transaction_model_predicts_high_risk():
    model = TransactionDatasetModel()
    fraud_prob, confidence, _ = model.predict(
        {
            "amount": 50000,
            "merchant_category": "bank_transfer",
            "account_age_days": 2,
            "transactions_24h": 6,
            "payment_purpose": "investment",
            "beneficiary_verified": False,
            "unknown_requester": True,
            "otp_or_pin_requested": True,
            "link_or_qr_received": True,
        }
    )
    assert confidence > 0
    assert fraud_prob >= 0.7
