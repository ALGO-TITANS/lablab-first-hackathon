import os
from pathlib import Path
from typing import Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Safe CSV Analyst & Self-Healing AI Agent"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # "development", "production", "test"
    DEBUG: bool = True

    # Directories & Storage (Configurable for persistent disk mounts like Render /var/data)
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOADS_DIR: Path | None = None
    SAMPLE_DATA_DIR: Path = BASE_DIR / "sample_data"
    DB_PATH: Path | None = None

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

    # CORS Configuration: string (comma-separated), JSON list, or list of origins
    CORS_ORIGINS: Union[list[str], str, None] = None

    @model_validator(mode="after")
    def resolve_paths_and_env(self) -> "Settings":
        # Resolve UPLOADS_DIR and DB_PATH relative to DATA_DIR if not explicitly set
        if self.UPLOADS_DIR is None:
            self.UPLOADS_DIR = self.DATA_DIR / "uploads"
        if self.DB_PATH is None:
            self.DB_PATH = self.DATA_DIR / "metadata.db"

        # Production safety defaults: disable DEBUG unless explicitly forced
        is_prod = self.ENVIRONMENT.lower() == "production"
        if is_prod:
            if "DEBUG" not in os.environ:
                self.DEBUG = False

        # Resolve CORS origins
        raw = self.CORS_ORIGINS
        origins: list[str] = []
        if isinstance(raw, str):
            s = raw.strip()
            if s.startswith("[") and s.endswith("]"):
                import json
                try:
                    parsed = json.loads(s)
                    if isinstance(parsed, list):
                        origins = [str(x) for x in parsed]
                except Exception:
                    origins = [x.strip() for x in s.split(",") if x.strip()]
            else:
                origins = [x.strip() for x in s.split(",") if x.strip()]
        elif isinstance(raw, list):
            origins = [str(x) for x in raw]

        # Clean origins: strip trailing slashes, disallow wildcard "*", filter duplicates
        clean: list[str] = []
        for item in origins:
            cleaned_item = item.strip().rstrip("/")
            if cleaned_item and cleaned_item != "*" and cleaned_item not in clean:
                clean.append(cleaned_item)

        if is_prod:
            # Production: strictly use explicitly configured origins (never auto-inject localhost)
            self.CORS_ORIGINS = clean
        else:
            # Development / testing: retain localhost defaults
            for default_origin in DEFAULT_CORS_ORIGINS:
                if default_origin not in clean:
                    clean.append(default_origin)
            self.CORS_ORIGINS = clean

        return self

    def ensure_directories(self) -> None:
        """Safely create storage directories at startup."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        if self.UPLOADS_DIR:
            self.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        if self.DB_PATH:
            self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
