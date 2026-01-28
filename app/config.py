import os

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_API_BASE = os.getenv("GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta/openai/")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True") == "True"
    
    MODEL_MAPPING = {
        "local-model": "gemini-2.5-flash",
        "gpt-4": "gemini-2.5-pro",
        "gpt-3.5-turbo": "gemini-2.5-flash",
        "default": "gemini-2.5-flash"
    }
