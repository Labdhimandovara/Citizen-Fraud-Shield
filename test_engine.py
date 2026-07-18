#!/usr/bin/env python3
from verification_engine_v2 import EnhancedVerificationEngineV3

print("\n" + "="*60)
print("Testing Fraud Detection Engine")
print("="*60)

engine = EnhancedVerificationEngineV3()

# TEST 1: FAKE CURRENCY
print("\n📸 TEST 1: FAKE CURRENCY")
print("-"*60)
result = engine.verify("currency", {
    "denomination": "500",
    "image_base64": "A" * 3000
})
print(f"Risk: {result.risk_level.value}")
print(f"Fraud Prob: {result.fraud_probability*100:.1f}%")
print(f"Expected: HIGH RISK ✅")

# TEST 2: SCAM CALL
print("\n📞 TEST 2: DIGITAL ARREST SCAM")
print("-"*60)
scam = "This is CBI. Transfer funds immediately or you'll be arrested. Do not tell anyone."
result = engine.verify("call", {"transcript": scam})
print(f"Risk: {result.risk_level.value}")
print(f"Fraud Prob: {result.fraud_probability*100:.1f}%")
print(f"Expected: HIGH RISK (>90%) ✅")

# TEST 3: OTP PHISHING
print("\n💳 TEST 3: OTP PHISHING TRANSACTION")
print("-"*60)
txn = {
    "amount": 50000,
    "account_age_days": 5,
    "unknown_requester": True,
    "otp_or_pin_requested": True,
}
result = engine.verify("transaction", {"transaction": txn})
print(f"Risk: {result.risk_level.value}")
print(f"Fraud Prob: {result.fraud_probability*100:.1f}%")
print(f"Expected: HIGH RISK (>70%) ✅")

# TEST 4: LEGITIMATE CALL
print("\n✅ TEST 4: LEGITIMATE CALL")
print("-"*60)
legit = "Hi, customer service. We have a new plan. Are you interested?"
result = engine.verify("call", {"transcript": legit})
print(f"Risk: {result.risk_level.value}")
print(f"Fraud Prob: {result.fraud_probability*100:.1f}%")
print(f"Expected: LOW RISK (<30%) ✅")

print("\n" + "="*60)
print("✅ All tests complete!")
print("="*60)