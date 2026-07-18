# Citizen Fraud Shield

Citizen Fraud Shield is a dataset-backed fraud-risk system with a FastAPI backend and Streamlit dashboard for:

- transaction fraud detection
- currency authenticity detection
- call scam detection

The live backend now uses only the trained model artifacts in `models/` and returns `VERIFY` when a model is missing, unreadable, or not confident enough.

## Project layout

- `main.py` — FastAPI backend
- `dashboard.py` — Streamlit UI
- `verification_engine_v2.py` — dataset-backed verification engine
- `dataset_models.py` — model loaders and feature preprocessing
- `train_models.py` — model training script
- `models/` — saved `.joblib` model bundles
- `ARCHITECTURE.md` — full module and data-flow description

## Required local datasets

Transaction:

- `paysim.csv`

Currency:

- `currency_dataset/training/real`
- `currency_dataset/training/fake`
- `currency_dataset/validation/real`
- `currency_dataset/validation/fake`
- `currency_dataset/testing/real`
- `currency_dataset/testing/fake`

Call:

- `SMSSpamCollection` (SMS Spam Collection) in the project root, used as the text fraud corpus for the call module

## Train the models

Run training after the datasets are in place:

```powershell
venv\Scripts\python.exe train_models.py --transactions paysim.csv --currency-root currency_dataset --calls SMSSpamCollection
```

This writes:

- `models/transaction_fraud.joblib`
- `models/currency_authenticity.joblib`
- `models/call_fraud.joblib`
- `models/registry.json`
- `models/artifacts/*.png`

The saved bundles include model metadata and validation/test metrics.

## Run the app

Start the backend:

```powershell
venv\Scripts\python.exe main.py
```

Start the dashboard in another terminal:

```powershell
venv\Scripts\streamlit.exe run dashboard.py
```

API docs:

- `http://localhost:8000/docs`

## What the backend now does

- Uses trained ML models instead of fixed risk scoring for transaction, currency, and call checks.
- Returns `VERIFY` with `confidence: 0` when a model is unavailable or inference fails.
- Stores alert history in `fraud_alerts.db`.
- Exposes model version and evaluation metrics in API responses.

## Current limitation

The transaction and currency models are trained from your local datasets and are fully dataset-backed.
The call model currently falls back to the lightweight transcript dataset generated inside `train_models.py` if you do not provide a labelled call dataset file.

## Safety note

This tool supports a human decision and does not prove a note, payee, or caller is legitimate. For suspicious payments, verify through official bank channels.
