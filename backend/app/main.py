from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.database import init_db
from app.api.datasets import router as datasets_router
from app.api.analysis import router as analysis_router
from app.api.stats import router as stats_router
from app.api.settings import router as settings_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure directories and initialize SQLite database
    settings.ensure_directories()
    init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Safe CSV Analytics Platform with Self-Healing AI Execution Sandbox",
    lifespan=lifespan
)

# CORS (configured via CORS_ORIGINS; wildcard '*' strictly removed for deployment security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(datasets_router)
app.include_router(analysis_router)
app.include_router(stats_router)
app.include_router(settings_router)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "default_provider": settings.DEFAULT_LLM_PROVIDER,
        "sandbox_timeout_seconds": settings.SANDBOX_TIMEOUT_SECONDS
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
