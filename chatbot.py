"""Gemini-powered fraud-prevention assistant."""

import os
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv(".env")
# Some early project setups placed the key in .env.example. Support that file
# during migration, while treating the documented placeholder as unset.
if not os.getenv("GEMINI_API_KEY"):
    load_dotenv(".env.example")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY.lower().startswith("your_"):
    GEMINI_API_KEY = ""
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
GEMINI_BASE_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)

FRAUD_CONTEXT = """
You are Citizen Fraud Shield, a fraud-prevention assistant for Indian citizens.
Give practical, concise, safety-first guidance. Never ask for OTPs, PINs,
passwords, CVV, Aadhaar numbers, or bank credentials. Explain warning signs,
safe verification steps, and how to report urgent cases to NCRP on 1930.
Use the user's selected language. Do not claim that a payment is certainly safe
or fraudulent without evidence.
""".strip()


class GeminiClient:
    """Minimal Gemini REST client; Gemini is the only supported LLM backend."""

    def is_available(self) -> bool:
        return bool(GEMINI_API_KEY)

    def generate(self, contents: list[dict]) -> str:
        response = requests.post(
            GEMINI_BASE_URL,
            headers={"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY},
            json={
                "contents": contents,
                "systemInstruction": {"parts": [{"text": FRAUD_CONTEXT}]},
                "generationConfig": {"maxOutputTokens": 800, "temperature": 0.4},
            },
            timeout=60,
        )
        if not response.ok:
            return f"Gemini could not respond right now (HTTP {response.status_code}). Please try again."
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError):
            return "Gemini returned an empty response. Please try again."


class FraudAwarenessBot:
    """Conversation manager backed exclusively by Gemini."""

    def __init__(self):
        self.gemini = GeminiClient()
        self.conversation_history: list[dict] = []

    def respond(self, user_message: str, language: str = "en") -> str:
        if not self.gemini.is_available():
            return "Gemini is not configured. Add GEMINI_API_KEY to your .env file, then restart the API server."

        contents = []
        for exchange in self.conversation_history[-5:]:
            contents.extend([
                {"role": "user", "parts": [{"text": exchange["user"]}]},
                {"role": "model", "parts": [{"text": exchange["assistant"]}]},
            ])
        contents.append({"role": "user", "parts": [{"text": f"Respond in {language}.\n\n{user_message}"}]})
        answer = self.gemini.generate(contents)
        self.conversation_history.append({"user": user_message, "assistant": answer, "timestamp": datetime.now().isoformat()})
        return answer

    def get_status(self) -> dict:
        return {"gemini": self.gemini.is_available(), "active_backend": "gemini" if self.gemini.is_available() else None}

    def get_helpful_resources(self, language: str = "en") -> list[dict]:
        return [
            {"label": "Cybercrime Helpline", "value": "1930"},
            {"label": "Cybercrime Portal", "value": "https://cybercrime.gov.in"},
        ]
