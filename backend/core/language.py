"""Language detection and translation module."""
import os
import httpx
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from dotenv import load_dotenv

load_dotenv()

INDIAN_LANGS = {'hi', 'bn', 'gu', 'kn', 'ml', 'mr', 'pa', 'ta', 'te', 'ur'}

def detect_and_translate(text: str) -> dict:
    """Detect language and translate non-English text to English using Sarvam API."""
    if len(text) < 20:
        return {
            "original_language": "unknown",
            "translated_text": text,
            "was_translated": False
        }
        
    try:
        lang = detect(text)
    except LangDetectException:
        return {
            "original_language": "unknown",
            "translated_text": text,
            "was_translated": False
        }
        
    if lang == "en":
        return {
            "original_language": "en",
            "translated_text": text,
            "was_translated": False
        }
        
    source_lang = f"{lang}-IN" if lang in INDIAN_LANGS else lang
    
    url = "https://api.sarvam.ai/translate"
    headers = {
        "api-subscription-key": os.getenv("SARVAM_API_KEY", ""),
        "Content-Type": "application/json"
    }
    payload = {
        "input": text,
        "source_language_code": source_lang,
        "target_language_code": "en-IN",
        "model": "mayura:v1",
        "enable_preprocessing": True
    }
    
    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        translated_text = data.get("translated_text", text)
        return {
            "original_language": lang,
            "translated_text": translated_text,
            "was_translated": True
        }
    except Exception as e:
        print(f"[WARNING] detect_and_translate: Translation failed - {e}")
        return {
            "original_language": lang,
            "translated_text": text,
            "was_translated": False
        }

if __name__ == "__main__":
    test_str = "यह परीक्षा का प्रश्न है।"
    print("Test string:", test_str)
    res = detect_and_translate(test_str)
    print("Response:", res)
