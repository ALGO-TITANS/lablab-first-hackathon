from fastapi import APIRouter
from app.config import settings
from app.schemas.settings import AppSettings, UpdateSettingsRequest

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("", response_model=AppSettings)
def get_current_settings():
    return AppSettings(
        default_llm_provider=settings.DEFAULT_LLM_PROVIDER,
        gemini_api_key_configured=bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 5),
        gemini_model=settings.GEMINI_MODEL,
        openai_api_key_configured=bool(settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY) > 5),
        openai_base_url=settings.OPENAI_BASE_URL,
        openai_model=settings.OPENAI_MODEL,
        sandbox_timeout_seconds=settings.SANDBOX_TIMEOUT_SECONDS,
        sandbox_max_memory_mb=settings.SANDBOX_MAX_MEMORY_MB,
        sandbox_max_output_chars=settings.SANDBOX_MAX_OUTPUT_CHARS,
        max_repair_attempts=settings.MAX_REPAIR_ATTEMPTS
    )

@router.post("", response_model=AppSettings)
def update_settings(payload: UpdateSettingsRequest):
    if payload.default_llm_provider is not None:
        settings.DEFAULT_LLM_PROVIDER = payload.default_llm_provider
    if payload.gemini_api_key is not None:
        settings.GEMINI_API_KEY = payload.gemini_api_key
    if payload.gemini_model is not None:
        settings.GEMINI_MODEL = payload.gemini_model
    if payload.openai_api_key is not None:
        settings.OPENAI_API_KEY = payload.openai_api_key
    if payload.openai_base_url is not None:
        settings.OPENAI_BASE_URL = payload.openai_base_url
    if payload.openai_model is not None:
        settings.OPENAI_MODEL = payload.openai_model
    if payload.sandbox_timeout_seconds is not None:
        settings.SANDBOX_TIMEOUT_SECONDS = payload.sandbox_timeout_seconds

    return get_current_settings()
