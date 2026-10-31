from typing import Optional
from pydantic import BaseModel

class AppSettings(BaseModel):
    default_llm_provider: str
    gemini_api_key_configured: bool
    gemini_model: str
    openai_api_key_configured: bool
    openai_base_url: str
    openai_model: str
    sandbox_timeout_seconds: float
    sandbox_max_memory_mb: int
    sandbox_max_output_chars: int
    max_repair_attempts: int

class UpdateSettingsRequest(BaseModel):
    default_llm_provider: Optional[str] = None
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    openai_model: Optional[str] = None
    sandbox_timeout_seconds: Optional[float] = None
