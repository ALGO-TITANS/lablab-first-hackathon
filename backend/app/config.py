import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Safe CSV Analyst & Self-Healing AI Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Directories
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOADS_DIR: Path = BASE_DIR / "data" / "uploads"
    SAMPLE_DATA_DIR: Path = BASE_DIR / "sample_data"
    DB_PATH: Path = BASE_DIR / "data" / "metadata.db"

    # Execution & Sandbox Limits
    MAX_UPLOAD_SIZE_MB: int = 50
    SANDBOX_TIMEOUT_SECONDS: float = 8.0
    SANDBOX_MAX_MEMORY_MB: int = 512
    SANDBOX_MAX_OUTPUT_CHARS: int = 200000
    MAX_REPAIR_ATTEMPTS: int = 2

    # AI Provider Configuration
    DEFAULT_LLM_PROVIDER: str = "mock"  # "mock", "gemini", "openai"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]

settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
