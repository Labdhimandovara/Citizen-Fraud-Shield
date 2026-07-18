"""
Test Scenarios & Demo Data for Trust Verification Engine
Run this to quickly populate the system with test cases
"""

from verification_engine_v2 import TrustVerificationEngine
import json
from datetime import datetime

# Initialize engine
engine = TrustVerificationEngine()

# ================== TEST DATA ==================

# High-Risk Scam Transcripts
HIGH_RISK_SCAMS = [
    {
        "name": "Classic CBI Scam",
        "transcript": """
        Hello sir/madam, this is CBI calling. We have found serious illegal activity 
        on your bank account. Money laundering investigation. You must immediately 
        transfer all your money to a safe government account for verification. 
        Do not tell anyone about this call. This is urgent, you have 1 hour to act.
        """
    },
    {
        "name": "ED Threat",
        "transcript": """
        This is ED - Enforcement Directorate. Your account is linked to a criminal case. 
        All your assets will be seized unless you provide secure amount immediately. 
        Transfer Rs 500,000 to this account number now. Keep this confidential.
        """
    },
    {
        "name": "Customs Impersonation",
        "transcript": """
        Namaste, this is Customs department. Your parcel contains illegal items. 
        You are liable for penalty of Rs 2,00,000. Pay immediately or face arrest warrant.
        """
    },
]

# Low-Risk Legitimate Calls
LOW_RISK_CALLS = [
    {
        "name": "Bank Verification Call",
        "transcript": """
        Hello, this is HDFC Bank customer service. We are calling to confirm 
        if you made a transaction of Rs 5000 at 2 PM today. Did you authorize this?
        """
    },
    {
        "name": "OTP Verification",
        "transcript": """
        Your OTP for verification is 123456. This code is valid for 10 minutes. 
        Do not share with anyone.
        """
    },
]

# High-Risk Transactions
HIGH_RISK_TRANSACTIONS = [
    {
        "name": "New Account, Sudden Large Transfer",
        "data": {
            "amount": 500000,
            "account_age_days": 3,
            "transactions_last_24h": 12,
            "user_avg_transaction_amount": 10000,
            "amount_deviation_percent": 5000,
            "receiver_account_age_days": 1,
            "is_cross_country": True
        }
    },
    {
        "name": "Rapid Multiple Transfers",
        "data": {
            "amount": 100000,
            "account_age_days": 7,
            "transactions_last_24h": 25,
            "user_avg_transaction_amount": 50000,
            "receiver_account_age_days": 2,
            "is_cross_country": True
        }
    },
    {
        "name": "Mule Account Pattern",
        "data": {
            "amount": 250000,
            "account_age_days": 2,
            "transactions_last_24h": 8,
            "user_avg_transaction_amount": 0,
            "receiver_account_age_days": 1,
            "is_cross_country": True
        }
    },
]

# Legitimate Transactions
LEGITIMATE_TRANSACTIONS = [
    {
        "name": "Regular Salary Deposit",
        "data": {
            "amount": 50000,
            "account_age_days": 365,
            "transactions_last_24h": 1,
            "user_avg_transaction_amount": 45000,
            "receiver_account_age_days": 180,
            "is_cross_country": False
        }
    },
    {
        "name": "Expected Payment to Known Vendor",
        "data": {
            "amount": 100000,
            "account_age_days": 730,
            "transactions_last_24h": 2,
            "user_avg_transaction_amount": 95000,
            "receiver_account_age_days": 365,
            "is_cross_country": False
        }
    },
]

# ================== TEST RUNNER ==================

def run_all_tests():
    """Run all test scenarios and display results"""
    
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║   Trust Verification Engine - Test Suite              ║
    ║   Running all scenarios...                             ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    # Test 1: High-Risk Scam Calls
    print("\n" + "="*60)
    print("TEST 1: HIGH-RISK SCAM DETECTION")
    print("="*60)
    
    for scam in HIGH_RISK_SCAMS:
        print(f"\n📞 Testing: {scam['name']}")
        result = engine.verify("call", {"transcript": scam['transcript']})
        print(f"   Trust Score: {result.trust_score:.1f}/100")
        print(f"   Risk Level: {result.risk_level.value}")
        print(f"   Action: {result.action}")
        print(f"   ✅ PASS" if result.risk_level.value == "HIGH" else f"   ❌ FAIL")
    
    # Test 2: Legitimate Calls
    print("\n" + "="*60)
    print("TEST 2: LEGITIMATE CALL DETECTION")
    print("="*60)
    
    for call in LOW_RISK_CALLS:
        print(f"\n📞 Testing: {call['name']}")
        result = engine.verify("call", {"transcript": call['transcript']})
        print(f"   Trust Score: {result.trust_score:.1f}/100")
        print(f"   Risk Level: {result.risk_level.value}")
        print(f"   Action: {result.action}")
        print(f"   ✅ PASS" if result.risk_level.value in ["LOW", "MEDIUM"] else f"   ❌ FAIL")
    
    # Test 3: High-Risk Transactions
    print("\n" + "="*60)
    print("TEST 3: FRAUD TRANSACTION DETECTION")
    print("="*60)
    
    for txn in HIGH_RISK_TRANSACTIONS:
        print(f"\n💰 Testing: {txn['name']}")
        result = engine.verify("transaction", {"transaction": txn['data']})
        print(f"   Trust Score: {result.trust_score:.1f}/100")
        print(f"   Risk Level: {result.risk_level.value}")
        print(f"   Anomalies: {result.detailed_factors.get('anomaly_flags', [])}")
        print(f"   ✅ PASS" if result.risk_level.value == "HIGH" else f"   ❌ FAIL")
    
    # Test 4: Legitimate Transactions
    print("\n" + "="*60)
    print("TEST 4: LEGITIMATE TRANSACTION DETECTION")
    print("="*60)
    
    for txn in LEGITIMATE_TRANSACTIONS:
        print(f"\n💰 Testing: {txn['name']}")
        result = engine.verify("transaction", {"transaction": txn['data']})
        print(f"   Trust Score: {result.trust_score:.1f}/100")
        print(f"   Risk Level: {result.risk_level.value}")
        print(f"   Action: {result.action}")
        print(f"   ✅ PASS" if result.risk_level.value in ["LOW", "MEDIUM"] else f"   ❌ FAIL")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    stats = engine.get_statistics(hours=24)
    print(f"\n📊 Total Verifications Logged: {stats['total_alerts']}")
    print(f"   High Risk: {stats['by_risk_level']['HIGH']}")
    print(f"   Medium Risk: {stats['by_risk_level']['MEDIUM']}")
    print(f"   Low Risk: {stats['by_risk_level']['LOW']}")
    
    # Alerts
    alerts = engine.get_recent_alerts(limit=5)
    print(f"\n📢 Recent Alerts: {len(alerts)}")
    for alert in alerts:
        print(f"   • {alert['timestamp']}: {alert['input_type']} - {alert['action']}")
    
    print("\n✅ All tests completed!")

def demo_single_scenario(scenario_type: str, scenario_name: str):
    """Run a single demo scenario"""
    
    print(f"\n{'='*60}")
    print(f"DEMO: {scenario_name}")
    print(f"{'='*60}\n")
    
    if scenario_type == "high_risk_scam":
        scam = HIGH_RISK_SCAMS[0]
        print(f"📞 Call: {scam['name']}")
        print(f"Transcript: {scam['transcript'][:100]}...")
        result = engine.verify("call", {"transcript": scam['transcript']})
    
    elif scenario_type == "legitimate_call":
        call = LOW_RISK_CALLS[0]
        print(f"📞 Call: {call['name']}")
        print(f"Transcript: {call['transcript'][:100]}...")
        result = engine.verify("call", {"transcript": call['transcript']})
    
    elif scenario_type == "fraud_txn":
        txn = HIGH_RISK_TRANSACTIONS[0]
        print(f"💰 Transaction: {txn['name']}")
        print(f"Amount: Rs {txn['data']['amount']}")
        print(f"Account Age: {txn['data']['account_age_days']} days")
        result = engine.verify("transaction", {"transaction": txn['data']})
    
    elif scenario_type == "legitimate_txn":
        txn = LEGITIMATE_TRANSACTIONS[0]
        print(f"💰 Transaction: {txn['name']}")
        print(f"Amount: Rs {txn['data']['amount']}")
        print(f"Account Age: {txn['data']['account_age_days']} days")
        result = engine.verify("transaction", {"transaction": txn['data']})
    
    else:
        print(f"Unknown scenario: {scenario_type}")
        return
    
    # Display result
    print(f"\n{'─'*60}")
    print(f"RESULT:")
    print(f"{'─'*60}")
    print(f"Trust Score: {result.trust_score:.2f}/100")
    print(f"Risk Level: {result.risk_level.value}")
    print(f"Action: {result.action}")
    print(f"\nRecommendation:")
    print(f"{result.recommendation}")
    print(f"\nDetailed Factors:")
    print(json.dumps(result.detailed_factors, indent=2))

# ================== MENU ==================

if __name__ == "__main__":
    import sys
    
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║   Trust Verification Engine - Test Suite              ║
    ║   Choose an option:                                   ║
    ║   1. Run all tests                                    ║
    ║   2. Demo: High-Risk Scam                             ║
    ║   3. Demo: Legitimate Call                            ║
    ║   4. Demo: Fraud Transaction                          ║
    ║   5. Demo: Legitimate Transaction                     ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("Enter choice (1-5): ").strip()
    
    if choice == "1":
        run_all_tests()
    elif choice == "2":
        demo_single_scenario("high_risk_scam", "High-Risk Scam Detection")
    elif choice == "3":
        demo_single_scenario("legitimate_call", "Legitimate Call Detection")
    elif choice == "4":
        demo_single_scenario("fraud_txn", "Fraud Transaction Detection")
    elif choice == "5":
        demo_single_scenario("legitimate_txn", "Legitimate Transaction Detection")
    else:
        print("Invalid choice")
