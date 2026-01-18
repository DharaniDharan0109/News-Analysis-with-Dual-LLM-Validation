import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    NEWSAPI_KEY: str = os.getenv("NEWSAPI_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")

    NEWSAPI_ENDPOINT: str = "https://newsapi.org/v2/everything"
    QUERY: str = os.getenv("QUERY", "India politics OR India government")
    PAGE_SIZE: int = int(os.getenv("PAGE_SIZE", "15"))

    # Gemini model (LLM#1)
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # OpenRouter model (LLM#2 validator)
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")

    OUTPUT_DIR: str = "output"


settings = Settings()
