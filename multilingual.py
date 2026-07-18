"""
Multilingual Support for Citizen Fraud Shield
Supports 12 Indian languages with automatic translation
"""

from typing import Dict, Any, Optional
import json

# ================== LANGUAGE CONFIGURATION ==================

SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "flag": "🇬🇧", "native": "English"},
    "hi": {"name": "Hindi", "flag": "🇮🇳", "native": "हिंदी"},
    "mr": {"name": "Marathi", "flag": "🇮🇳", "native": "मराठी"},
    "gu": {"name": "Gujarati", "flag": "🇮🇳", "native": "ગુજરાતી"},
    "bn": {"name": "Bengali", "flag": "🇮🇳", "native": "বাংলা"},
    "ta": {"name": "Tamil", "flag": "🇮🇳", "native": "தமிழ்"},
    "te": {"name": "Telugu", "flag": "🇮🇳", "native": "తెలుగు"},
    "kn": {"name": "Kannada", "flag": "🇮🇳", "native": "ಕನ್ನಡ"},
    "ml": {"name": "Malayalam", "flag": "🇮🇳", "native": "മലയാളം"},
    "pa": {"name": "Punjabi", "flag": "🇮🇳", "native": "ਪੰਜਾਬੀ"},
    "od": {"name": "Odia", "flag": "🇮🇳", "native": "ଓଡ଼ିଆ"},
    "as": {"name": "Assamese", "flag": "🇮🇳", "native": "অসমীয়া"}
}

# ================== TRANSLATIONS DICTIONARY ==================

TRANSLATIONS = {
    "verify_call": {
        "en": "Verify Call",
        "hi": "कॉल सत्यापित करें",
        "mr": "कॉल सत्यापित करा",
        "gu": "કૉલ ચકાસો",
        "bn": "কল যাচাই করুন",
        "ta": "அழைப்பை சரிபார்க்கவும்",
        "te": "కాల్‌ను ధృవీకరించండి",
        "kn": "ಕಾಲ್ ಅನ್ನು ಪರಿಶೀಲಿಸಿ",
        "ml": "കോൾ സ്ഥിരീകരിക്കുക",
        "pa": "ਕਾਲ ਦੀ ਪੁष्टि ਕਰੋ",
        "od": "ଏକ ଜାଗା ଆମାନ୍ତ୍ରଣ",
        "as": "কল যাচাই কৰক"
    },
    "verify_currency": {
        "en": "Verify Currency",
        "hi": "मुद्रा सत्यापित करें",
        "mr": "चलन सत्यापित करा",
        "gu": "કરન્સી ચકાસો",
        "bn": "মুদ্রা যাচাই করুন",
        "ta": "கொடுப்பனவை சரிபார்க்கவும்",
        "te": "కరెన్సీని ధృవీకరించండి",
        "kn": "ಸ್ಥಳೀಯ ಅಮೆರಿಕನ್ ವಿನಿಮಯ ಪರಿಶೀಲಿಸಿ",
        "ml": "കറൻസി സ്ഥിരീകരിക്കുക",
        "pa": "ਮੁਦਰਾ ਦੀ ਤਸਦੀਕ ਕਰੋ",
        "od": "ମୁଦ୍ରା ଯାଚାଇ",
        "as": "মুদ্রা পরীক্ষা কৰক"
    },
    "verify_transaction": {
        "en": "Verify Transaction",
        "hi": "लेनदेन सत्यापित करें",
        "mr": "व्यवहार सत्यापित करा",
        "gu": "વ્યવહાર ચકાસો",
        "bn": "লেনদেন যাচাই করুন",
        "ta": "பரிவர்த்தனையை சரிபார்க்கவும்",
        "te": "లావాదేవీని ధృవీకరించండి",
        "kn": "ವಹಿವಾಟಿ ಪರಿಶೀಲಿಸಿ",
        "ml": "ഇടപാട് സ്ഥിരീകരിക്കുക",
        "pa": "ਲੈਨਦੇਨ ਦੀ ਤਸਦੀਕ ਕਰੋ",
        "od": "ଲେଣ୍ଡେଣ୍ଡ ଯାଚାଇ",
        "as": "লেনদেন পরীক্ষা কৰক"
    },
    "high_risk": {
        "en": "🔴 HIGH RISK",
        "hi": "🔴 उच्च जोखिम",
        "mr": "🔴 उच्च धोका",
        "gu": "🔴 ઊચ્ચ જોખમ",
        "bn": "🔴 উচ্চ ঝুঁকি",
        "ta": "🔴 அதிக ஆபத்து",
        "te": "🔴 అధిక ఝুఁఖిమ",
        "kn": "🔴 ಹೆಚ್ಚು ಅಪಾಯ",
        "ml": "🔴 ഉയർന്ന അപകടം",
        "pa": "🔴 ਉੱਚ ਖ਼ਤਰਾ",
        "od": "🔴 ଉଚ୍ଚ ଝୁଁକି",
        "as": "🔴 উচ্চ ঝুঁকি"
    },
    "medium_risk": {
        "en": "🟡 MEDIUM RISK",
        "hi": "🟡 मध्यम जोखिम",
        "mr": "🟡 मध्यम धोका",
        "gu": "🟡 મધ્યમ જોખમ",
        "bn": "🟡 মধ্যম ঝুঁকি",
        "ta": "🟡 நடுத்தர ஆபத்து",
        "te": "🟡 మధ్యమ ఝుఁఖిమ",
        "kn": "🟡 ಮಧ್ಯಮ ಅಪಾಯ",
        "ml": "🟡 ഇടത്തരം അപകടം",
        "pa": "🟡 ਮੱਧਮ ਖ਼ਤਰਾ",
        "od": "🟡 ମଧ୍ୟମ ଝୁଁକି",
        "as": "🟡 মধ্যম ঝুঁকি"
    },
    "low_risk": {
        "en": "🟢 LOW RISK",
        "hi": "🟢 कम जोखिम",
        "mr": "🟢 कमी धोका",
        "gu": "🟢 ઓછો જોખમ",
        "bn": "🟢 কম ঝুঁকি",
        "ta": "🟢 குறைந்த ஆபத்து",
        "te": "🟢 తక్కువ ఝుఁఖిమ",
        "kn": "🟢 ಕಡಿಮೆ ಅಪಾಯ",
        "ml": "🟢 കുറഞ്ഞ അപകടം",
        "pa": "🟢 ਘੱਟ ਖ਼ਤਰਾ",
        "od": "🟢 ନିମ୍ନ ଝୁଁକି",
        "as": "🟢 কম ঝুঁকি"
    },
    "hang_up": {
        "en": "HANG UP IMMEDIATELY",
        "hi": "तुरंत कॉल काट दें",
        "mr": "लगेच कॉल कापा",
        "gu": "તરત જ કૉલ કાપો",
        "bn": "অবিলম্বে কল কেটে দিন",
        "ta": "உடனடியாக அழைப்பை வெட்டவும்",
        "te": "వెంటనే కాల్‌ను కట్ చేయండి",
        "kn": "ತಕ್ಷಣ ಕರೆಯನ್ನು ಕತ್ತರಿಸಿ",
        "ml": "ഉടനെ കോൾ കട്ട് ചെയ്യുക",
        "pa": "ਤੁਰੰਤ ਕਾਲ ਕਿਤੁ ਦਿਓ",
        "od": "ତୋ ଅଫ୍ ଗ୍ରିଡ",
        "as": "অবিলম্বে কল কাট কৰক"
    },
    "scam_detected": {
        "en": "Scam detected. Do not share personal information.",
        "hi": "धोखाधड़ी का पता चला। व्यक्तिगत जानकारी साझा न करें।",
        "mr": "घोटाळा सापडला. व्यक्तिगत माहिती शेअर करू नका.",
        "gu": "છેતરપણ મળ્યું. ખાનગી માહિતી શેર કરશો નહીં.",
        "bn": "প্রতারণা সনাক্ত হয়েছে। ব্যক্তিগত তথ্য শেয়ার করবেন না।",
        "ta": "மோசடி கண்டறிய. ব্যক্তিগত தথ্য பகிர வேண்டாம்.",
        "te": "చక్కి కనుగొనబడింది. వ్యక్తిగత సమాచారం భాగస్వామ్యం చేయవద్దు.",
        "kn": "ವಂಚನೆ ಕಂಡುಹಿಡಿಯಲಾಗಿದೆ. ವ್ಯಕ್ತಿಗತ ಮಾಹಿತಿ ಹಂಚಿಕೊಳ್ಳಬೇಡಿ.",
        "ml": "കെണി കണ്ടെത്തിയെ. വ്യക്തിഗത വിവരങ്ങൾ പങ്കിടരുത്.",
        "pa": "ਧੋਖਾ ਖੋਜਿਆ ਗਿਆ। ਨਿੱਜੀ ਜਾਣਕਾਰੀ ਸਾਂਝੀ ਨਾ ਕਰੋ।",
        "od": "ଧୋଖା ଖୋଜି ଦିଆଗଲା। ବ୍ୟକ୍ତିଗତ ତଥ୍ୟ ସାଂଝା କରନୁଁ।",
        "as": "ধোকা ধৰা পৰিল। ব্যক্তিগত তথ্য শেয়াৰ কৰবলৈ নিদিওক।"
    },
    "report_to_ncrp": {
        "en": "Report to NCRP: https://cybercrime.gov.in or call 1930",
        "hi": "NCRP को रिपोर्ट करें: https://cybercrime.gov.in या 1930 पर कॉल करें",
        "mr": "NCRP ला अहवाल द्या: https://cybercrime.gov.in किंवा 1930 ला कॉल करा",
        "gu": "NCRP ને જણાવો: https://cybercrime.gov.in અથવા 1930 પર કૉલ કરો",
        "bn": "NCRP-কে রিপোর্ট করুন: https://cybercrime.gov.in বা 1930 এ কল করুন",
        "ta": "NCRP க்கு அறிவிக்கவும்: https://cybercrime.gov.in அல்லது 1930 ஐ அழைக்கவும்",
        "te": "NCRP కి నివేదించండి: https://cybercrime.gov.in లేదా 1930 కి కాల్ చేయండి",
        "kn": "NCRP ಗೆ ವರದಿ ಮಾಡಿ: https://cybercrime.gov.in ಅಥವಾ 1930 ಗೆ ಕರೆ ಮಾಡಿ",
        "ml": "NCRP-ക്കെ റിപ്പോർട്ട് ചെയ്യുക: https://cybercrime.gov.in അല്ലെങ്കിൽ 1930 ഇ വിളിക്കുക",
        "pa": "NCRP ਨੂੰ ਰਿਪੋਰਟ ਕਰੋ: https://cybercrime.gov.in ਜਾ 1930 'ਤੇ ਕਾਲ ਕਰੋ",
        "od": "NCRP କୁ ରିପୋର୍ଟ କରନ୍ତୁ: https://cybercrime.gov.in ବା 1930 କୁ କୋ",
        "as": "NCRP লৈ প্ৰতিবেদন দিয়াওক: https://cybercrime.gov.in বা 1930 লৈ ফোন কৰক"
    }
}

# ================== TRANSLATION ENGINE ==================

class MultilingualTranslator:
    """Handles all translations for Citizen Fraud Shield"""
    
    def __init__(self):
        self.translations = TRANSLATIONS
        self.default_language = "en"
    
    def translate(self, key: str, language: str = "en") -> str:
        """
        Get translated text for a key.
        
        Args:
            key: Translation key (e.g., "high_risk")
            language: Language code (e.g., "en", "hi", "mr")
        
        Returns:
            Translated text, or English fallback if not found
        """
        
        if key not in self.translations:
            return key  # Return key if not found
        
        if language not in self.translations[key]:
            return self.translations[key].get(self.default_language, key)
        
        return self.translations[key][language]
    
    def get_supported_languages(self) -> Dict[str, Dict]:
        """Get list of all supported languages"""
        return SUPPORTED_LANGUAGES
    
    def translate_result(self, result: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
        """
        Translate an entire verification result.
        
        Args:
            result: Verification result dict
            language: Target language code
        
        Returns:
            Translated result
        """
        
        if language == "en":
            return result  # English is default, no translation needed
        
        # Create a copy to avoid modifying original
        translated = result.copy()
        
        # Translate key fields
        translated_recommendation = self._translate_recommendation(
            result.get("recommendation", ""), 
            language
        )
        translated["recommendation"] = translated_recommendation
        
        # Translate risk level
        risk_key = f"{result['risk_level'].lower()}_risk"
        if risk_key in self.translations:
            translated["risk_level_text"] = self.translate(risk_key, language)
        
        return translated
    
    def _translate_recommendation(self, recommendation: str, language: str) -> str:
        """Translate recommendation text"""
        
        # Try to find matching recommendation and translate it
        for key, translations in self.translations.items():
            if "recommendation" in key or "report" in key:
                if translations.get("en") and translations["en"] in recommendation:
                    return translations.get(language, translations["en"])
        
        # Fallback: return original (in production, use Google Translate API)
        return recommendation
    
    def get_language_name(self, lang_code: str) -> str:
        """Get display name of language"""
        return SUPPORTED_LANGUAGES.get(lang_code, {}).get("name", lang_code)
    
    def get_language_flag(self, lang_code: str) -> str:
        """Get flag emoji for language"""
        return SUPPORTED_LANGUAGES.get(lang_code, {}).get("flag", "🌐")


# ================== HELPER FUNCTIONS ==================

def get_translated_ui(language: str = "en") -> Dict[str, str]:
    """Get all UI strings in a specific language"""
    
    translator = MultilingualTranslator()
    
    ui_strings = {
        "app_name": "Citizen Fraud Shield",
        "tagline": "AI That Protects Before You Pay, Trust, or Respond",
        "verify_call": translator.translate("verify_call", language),
        "verify_currency": translator.translate("verify_currency", language),
        "verify_transaction": translator.translate("verify_transaction", language),
        "chat": translator.translate("chat", language),
    }
    
    return ui_strings


# ================== EXAMPLE USAGE ==================

if __name__ == "__main__":
    translator = MultilingualTranslator()
    
    # Get translation
    print(translator.translate("high_risk", "hi"))  # Hindi
    print(translator.translate("scam_detected", "mr"))  # Marathi
    
    # Get all languages
    languages = translator.get_supported_languages()
    print(f"Supported languages: {len(languages)}")
    for code, info in languages.items():
        print(f"  {info['flag']} {info['name']} ({code})")