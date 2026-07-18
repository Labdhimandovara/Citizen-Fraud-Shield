# 🚀 Quick Start Guide - Trust Verification Engine

Get the entire system running locally in **5 minutes**.

---

## 📋 Prerequisites

- **Python 3.9+** (check: `python --version`)
- **Git** (optional, for cloning)
- **Flutter** (for mobile app, optional)

---

## 🏗️ Project Structure

```
trust-verification-engine/
├── main.py                    # FastAPI server
├── verification_engine.py     # Core logic
├── dashboard.py               # Streamlit UI
├── flutter_main.dart         # Flutter app (optional)
├── pubspec.yaml              # Flutter config
├── requirements.txt          # Python dependencies
└── alerts.db                 # SQLite (auto-created)
```

---

## ⚡ Quick Start (2 Terminals)

### **Terminal 1: Start FastAPI Backend**

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run FastAPI server
python main.py

# OR
uvicorn main:app --reload --port 8000
```

✅ When you see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Backend is ready!**

---

### **Terminal 2: Start Streamlit Dashboard**

```bash
# Activate same venv (in new terminal)
source venv/bin/activate

# Run dashboard
streamlit run dashboard.py
```

✅ When you see:
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

**Dashboard is ready!**

---

## 🧪 Test the System (Open Browser)

### **Option 1: Streamlit Dashboard** (Easiest)
Go to: **http://localhost:8501**

1. Click **📞 Verify Call** tab
2. Paste this scam transcript:
   ```
   Hello, this is CBI calling. We've detected illegal activity on your account. 
   Money laundering investigation. You must transfer all funds immediately 
   to a secure government account. Do not tell anyone. This is urgent.
   ```
3. Click **Analyze Call**
4. See result: 🔴 **HIGH RISK**

### **Option 2: API (cURL)**

**Verify a Call:**
```bash
curl -X POST http://localhost:8000/verify/call \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Hello this is CBI. Your account is under investigation. Transfer money immediately."
  }'
```

**Verify a Transaction:**
```bash
curl -X POST http://localhost:8000/verify/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500000,
    "account_age_days": 3,
    "transactions_last_24h": 15,
    "receiver_account_age_days": 2
  }'
```

**Get Alerts:**
```bash
curl http://localhost:8000/alerts?limit=10
```

**Get Statistics:**
```bash
curl http://localhost:8000/stats?hours=24
```

---

## 📱 Flutter App (Optional)

### **Setup**

```bash
# Install Flutter (if not already done)
flutter --version

# Navigate to project
cd trust-verification-engine

# Create Flutter project structure
flutter create . --platforms=android,ios

# Copy flutter_main.dart to lib/main.dart
cp flutter_main.dart lib/main.dart

# Get dependencies
flutter pub get

# Run on emulator/phone
flutter run
```

### **For Android Emulator:**
Update localhost address in Flutter code:
```dart
final API_BASE_URL = "http://10.0.2.2:8000";  // Emulator's localhost
```

For physical device:
```dart
final API_BASE_URL = "http://YOUR_COMPUTER_IP:8000";
```

---

## 🎯 Demo Scenarios

### **Scenario 1: Detect Digital Arrest Scam**

**Input (Call Transcript):**
```
Hello, this is CBI. Your account is under surveillance for money laundering. 
You must immediately transfer all your savings to a government account for verification. 
Do not inform anyone. This is urgent. You have 1 hour.
```

**Output:**
- ✅ Trust Score: **15/100**
- ✅ Risk Level: **HIGH**
- ✅ Action: **BLOCK**
- ✅ Recommendation: *"HANG UP NOW. This is a digital arrest scam..."*

---

### **Scenario 2: Detect Fraud Transaction**

**Input (Transaction Data):**
```json
{
  "amount": 500000,
  "account_age_days": 5,
  "transactions_last_24h": 18,
  "user_avg_transaction_amount": 50000,
  "receiver_account_age_days": 2,
  "is_cross_country": true
}
```

**Output:**
- ✅ Trust Score: **25/100**
- ✅ Risk Level: **HIGH**
- ✅ Anomalies: `["New account (5 days old)", "High velocity (18 txns)", "Unusual amount (500000)"]`

---

### **Scenario 3: Legitimate Transaction**

**Input:**
```json
{
  "amount": 50000,
  "account_age_days": 365,
  "transactions_last_24h": 1,
  "user_avg_transaction_amount": 40000,
  "receiver_account_age_days": 200
}
```

**Output:**
- ✅ Trust Score: **95/100**
- ✅ Risk Level: **LOW**
- ✅ Action: **ALLOW**

---

## 📊 Dashboard Features

### **Home Tab:**
- Real-time statistics (total alerts, by risk level, by type)
- Pie charts & bar graphs
- Recent alerts table

### **Verify Call Tab:**
- Paste transcript
- Get instant scam detection
- View detailed analysis

### **Verify Transaction Tab:**
- Enter transaction details
- Fraud risk assessment
- View anomaly factors

### **Verify Currency Tab:**
- Upload note image (demo)
- Counterfeit detection (simulated)
- Security feature analysis

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/health` | Check API status |
| `POST` | `/verify/call` | Verify call transcript |
| `POST` | `/verify/currency` | Verify note image |
| `POST` | `/verify/transaction` | Verify transaction |
| `GET` | `/alerts` | Get recent alerts |
| `GET` | `/stats` | Get statistics |
| `GET` | `/docs` | Swagger API docs |

---

## 🐛 Troubleshooting

### **"Connection refused" error**
- Make sure FastAPI is running in Terminal 1
- Check port 8000 is not blocked: `lsof -i :8000` (Mac/Linux)

### **Streamlit shows "API Offline"**
- Verify FastAPI server is running
- Try accessing http://localhost:8000/health in browser

### **Flutter app can't reach backend**
- For Android emulator: Use `10.0.2.2` instead of `localhost`
- For physical phone: Use your computer's IP address
- Check firewall settings

### **Database locked error**
- Delete `alerts.db` to reset: `rm alerts.db`
- Backend will recreate it automatically

---

## 📈 Next Steps (Post-Hackathon)

1. **Real Data Integration**
   - Connect to NCRB cybercrime portal
   - Integrate with telecom APIs (Jio, Airtel)
   - Use real fraud transaction datasets

2. **Enhanced ML Models**
   - Fine-tune on real scam transcripts
   - Deploy TensorFlow Lite counterfeit detector
   - Build graph neural networks for fraud rings

3. **Scaling**
   - Deploy to AWS/Google Cloud
   - Add Redis for caching
   - PostgreSQL instead of SQLite

4. **Multi-Language Support**
   - Add 12 Indian language translations
   - Regional language voice guidance

5. **Integration**
   - WhatsApp Business API
   - IVR integration
   - Police/bank dashboards

---

## 📞 Support

**Issues?** Check these files:
- `main.py` - FastAPI errors
- `verification_engine.py` - Logic errors
- `dashboard.py` - UI errors

**Quick debug:**
```bash
# Check dependencies
pip list | grep -E "fastapi|streamlit|pandas"

# Test endpoint directly
python -c "from verification_engine import TrustVerificationEngine; e = TrustVerificationEngine(); print(e.verify('call', {'transcript': 'Hello CBI'}))"
```

---

## 🎬 Demo Video Script (2 minutes)

1. **Show Dashboard** (30 sec)
   - "This is our real-time verification hub showing alerts, stats, and verdicts"

2. **Live Test - Scam Call** (30 sec)
   - Paste transcript → Show HIGH RISK verdict + recommendation

3. **Live Test - Fraud Txn** (30 sec)
   - Enter transaction data → Show anomalies detected

4. **Show Code Architecture** (30 sec)
   - One unified engine handling all threats
   - Same codebase, different inputs

**Key Message:** *"Trust at Speed. Verification at Scale. Safety for All."*

---

**Happy Testing! 🚀**

Questions? Check README.md for full documentation.
