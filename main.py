"""
Citizen Fraud Shield - Updated FastAPI Backend
Uses Verification Engine V3 with improved fraud detection
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import base64
import os
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
import json

from verification_engine_v2 import EnhancedVerificationEngineV3, result_to_dict
from languages_comprehensive import MultilingualTranslator
from chatbot import FraudAwarenessBot

# ================== PYDANTIC MODELS ==================

class CallVerificationRequest(BaseModel):
    transcript: str
    language: str = "en"

class TransactionVerificationRequest(BaseModel):
    amount: float
    merchant_category: Optional[str] = None
    device_info: Optional[dict] = None
    location: Optional[str] = None
    account_age_days: int = 30
    transactions_24h: int = 0
    avg_transaction_amount: Optional[float] = None
    device_mismatch: bool = False
    geographic_mismatch: bool = False
    beneficiary_new: bool = False
    beneficiary_verified: bool = False
    payment_channel: str = "UPI"
    payment_purpose: str = "purchase"
    unknown_requester: bool = False
    otp_or_pin_requested: bool = False
    link_or_qr_received: bool = False
    language: str = "en"

class ChatRequest(BaseModel):
    message: str
    language: str = "en"

# ================== FASTAPI APP ==================

app = FastAPI(
    title="Citizen Fraud Shield API v3",
    description="AI-powered fraud prevention platform with improved accuracy",
    version="3.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines - NOW USING V3 WITH IMPROVED ACCURACY
engine = EnhancedVerificationEngineV3(db_path="fraud_alerts.db")
translator = MultilingualTranslator()
chatbot = FraudAwarenessBot()

# ================== HEALTH & INFO ==================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Citizen Fraud Shield v3",
        "version": "3.0.0",
        "improvement": "Dataset-backed fraud detection with safe VERIFY fallbacks",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """API documentation"""
    return {
        "service": "Citizen Fraud Shield v3",
        "tagline": "AI That Protects Before You Pay, Trust, or Respond",
        "version": "3.0.0",
        "improvements": [
            "Dataset-backed transaction, currency, and call models",
            "Safe VERIFY fallback when a model is unavailable",
            "Risk aggregation without fixed confidence shortcuts",
            "Production-oriented evaluation metadata"
        ],
        "endpoints": {
            "calls": {
                "verify_call": "POST /api/verify/call",
                "verify_call_recording": "POST /api/verify/call-recording"
            },
            "currency": {
                "verify_currency": "POST /api/verify/currency"
            },
            "transactions": {
                "verify_transaction": "POST /api/verify/transaction"
            },
            "chat": {
                "chat_with_ai": "POST /api/chat"
            },
            "info": {
                "languages": "GET /api/languages",
                "alerts": "GET /api/alerts",
                "statistics": "GET /api/stats"
            }
        },
        "docs": "/docs"
    }

# ================== LANGUAGE INFO ==================

@app.get("/api/languages")
async def get_languages():
    """Get list of supported languages"""
    try:
        languages = translator.get_supported_languages()
        return {
            "supported_languages": len(languages),
            "languages": [
                {
                    "code": code,
                    "name": info["name"],
                    "native": info["native"],
                    "flag": info["flag"]
                }
                for code, info in languages.items()
            ]
        }
    except Exception as e:
        return {
            "error": "Could not fetch languages",
            "fallback_languages": ["en", "hi", "mr", "gu", "ta", "te"]
        }

# ================== CALL VERIFICATION ==================

@app.post("/api/verify/call")
async def verify_call(request: CallVerificationRequest):
    """
    Verify a suspicious call transcript using improved fraud detection
    
    Example (Digital Arrest Scam):
    {
        "transcript": "Hello, this is CBI. We found illegal activity on your account. Transfer all funds immediately to a secure government account. Do not tell anyone.",
        "language": "en"
    }
    
    Example (OTP Phishing):
    {
        "transcript": "This is your bank. Please provide your OTP to verify your identity. Your account will be blocked if you don't verify.",
        "language": "en"
    }
    """
    try:
        result = engine.verify("call", {
            "transcript": request.transcript
        })
        
        response = result_to_dict(result)
        
        # Translate if needed
        if request.language != "en":
            response = translator.translate_result(response, request.language)
        
        return response
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/verify/call-recording")
async def verify_call_recording(
    file: Optional[UploadFile] = File(None),
    audio_base64: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    language: str = Form("en")
):
    """
    Verify a call recording (MP3, WAV, M4A, OGG)
    Production requires a real speech-to-text stage before text classification.
    """
    try:
        allowed_formats = ["audio/mpeg", "audio/wav", "audio/mp4", "audio/m4a", "audio/ogg", "audio/webm"]
        
        file_name = filename or (file.filename if file else "unknown")
        contents = None
        
        if file:
            if file.content_type not in allowed_formats and not file.filename.lower().endswith(('.mp3', '.wav', '.m4a', '.ogg')):
                raise ValueError(f"Unsupported format. Allowed: MP3, WAV, M4A, OGG")
            
            contents = await file.read()
            if not contents:
                raise ValueError("Empty audio file")
        
        elif audio_base64:
            try:
                contents = base64.b64decode(audio_base64)
                if not contents:
                    raise ValueError("Invalid base64 data")
            except Exception as e:
                raise ValueError(f"Invalid audio data: {str(e)}")
        
        else:
            raise ValueError("No audio file provided")
        
        transcription_status = "unavailable"
        if os.getenv("WHISPER_API_KEY") or os.getenv("OPENAI_API_KEY"):
            transcription_status = "not_integrated"

        result = engine.verify("call_recording", {
            "transcript": "",
            "audio_available": True,
            "transcription_status": transcription_status,
        })

        response = result_to_dict(result)
        response["audio_info"] = {
            "filename": file_name,
            "size_bytes": len(contents) if contents else 0,
            "transcription_status": transcription_status
        }
        
        if language != "en":
            response = translator.translate_result(response, language)
        
        return response
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================== CURRENCY VERIFICATION ==================

@app.post("/api/verify/currency")
async def verify_currency(
    denomination: str = Form("500"),
    language: str = Form("en"),
    image_file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None)
):
    """
    Verify a currency note image with improved detection
    
    Checks for:
    - Security thread
    - Watermark
    - Microprint
    - Color gradients
    - Image quality
    """
    try:
        image_b64 = image_base64
        
        if image_file:
            contents = await image_file.read()
            image_b64 = base64.b64encode(contents).decode('utf-8')
        
        if not image_b64:
            raise ValueError("No image provided")
        
        result = engine.verify("currency", {
            "denomination": denomination,
            "image_base64": image_b64
        })
        
        response = result_to_dict(result)
        
        if language != "en":
            response = translator.translate_result(response, language)
        
        return response
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================== TRANSACTION VERIFICATION ==================

@app.post("/api/verify/transaction")
async def verify_transaction(request: TransactionVerificationRequest):
    """
    Verify a transaction for fraud indicators
    
    CRITICAL FACTORS (High Risk):
    - unknown_requester: True -> +0.20 fraud probability
    - otp_or_pin_requested: True -> +0.35 fraud probability (HIGHEST)
    - link_or_qr_received: True -> +0.12 fraud probability
    - account_age_days < 7 -> +0.18 fraud probability
    
    Example (High Risk):
    {
        "amount": 50000,
        "account_age_days": 5,
        "unknown_requester": true,
        "otp_or_pin_requested": true,
        "language": "en"
    }
    
    Result: HIGH RISK (fraud_probability ≥ 0.70)
    
    Example (Low Risk):
    {
        "amount": 5000,
        "account_age_days": 365,
        "beneficiary_verified": true,
        "unknown_requester": false,
        "otp_or_pin_requested": false,
        "language": "en"
    }
    
    Result: LOW RISK (fraud_probability ≤ 0.40)
    """
    try:
        transaction_data = {
            "amount": request.amount,
            "merchant_category": request.merchant_category,
            "device_info": request.device_info or {},
            "location": request.location,
            "account_age_days": request.account_age_days,
            "transactions_24h": request.transactions_24h,
            "avg_transaction_amount": request.avg_transaction_amount,
            "device_mismatch": request.device_mismatch,
            "geographic_mismatch": request.geographic_mismatch,
            "beneficiary_new": request.beneficiary_new,
            "beneficiary_verified": request.beneficiary_verified,
            "payment_channel": request.payment_channel,
            "payment_purpose": request.payment_purpose,
            "unknown_requester": request.unknown_requester,
            "otp_or_pin_requested": request.otp_or_pin_requested,
            "link_or_qr_received": request.link_or_qr_received,
        }
        
        result = engine.verify("transaction", {"transaction": transaction_data})
        response = result_to_dict(result)
        
        if request.language != "en":
            response = translator.translate_result(response, request.language)
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================== AI CHATBOT ==================

@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    """
    Chat with Citizen Fraud Shield AI Assistant
    
    Example:
    {
        "message": "What is a digital arrest scam?",
        "language": "en"
    }
    """
    try:
        if not request.message.strip():
            raise ValueError("Message cannot be empty")
        
        response_text = chatbot.respond(
            request.message,
            language=request.language
        )
        
        return {
            "message": request.message,
            "response": response_text,
            "language": request.language,
            "timestamp": datetime.now().isoformat(),
            "helpful_links": chatbot.get_helpful_resources(request.language)
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================== ALERTS & STATISTICS ==================

@app.get("/api/alerts")
async def get_alerts(
    limit: int = 20,
    risk_level: Optional[str] = None,
    language: str = "en"
):
    """Get recent fraud alerts"""
    try:
        alerts = engine.get_recent_alerts(limit=limit, risk_level=risk_level)
        
        return {
            "count": len(alerts),
            "alerts": alerts,
            "language": language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_statistics(hours: int = 24):
    """Get statistics for fraud alerts"""
    try:
        stats = engine.get_statistics(hours=hours)
        
        return {
            "period_hours": hours,
            "timestamp": datetime.now().isoformat(),
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================== ERROR HANDLERS ==================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# ================== STARTUP/SHUTDOWN ==================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║   Citizen Fraud Shield - FastAPI Backend v3            ║
    ║   🛡️  AI That Protects Before You Pay                  ║
    ║   ✨ IMPROVED ACCURACY - Real Scam Patterns             ║
    ╚════════════════════════════════════════════════════════╝
    """)
    print("✅ Verification Engine V3 initialized (Improved Accuracy)")
    print("✅ Real scam pattern detection enabled")
    print("✅ Multilingual Support enabled (12 languages)")
    print("✅ AI Assistant ready")
    print("\nKEY IMPROVEMENTS:")
    print("  • Dataset-backed call, currency, and transaction models")
    print("  • Safe VERIFY fallback when confidence is unavailable")
    print("  • Structured evaluation metadata and model versioning")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Citizen Fraud Shield backend stopped")

# ================== RUN ==================

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║   Citizen Fraud Shield - FastAPI Server v3            ║
    ║   🛡️  Digital Safety Intelligence Platform            ║
    ╚════════════════════════════════════════════════════════╝
    
    Starting server on http://0.0.0.0:8000
    API Docs: http://localhost:8000/docs
    
    Improvements in v3:
    ✨ Real scam pattern detection
    ✨ Improved fraud probability scoring
    ✨ Better currency authentication
    """)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
