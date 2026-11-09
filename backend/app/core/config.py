import os
from pathlib import Path

# Clean IPv6 bracket from NO_PROXY to prevent httpx parse error
for env_key in ["NO_PROXY", "no_proxy"]:
    val = os.environ.get(env_key)
    if val:
        cleaned = ",".join([h.strip() for h in val.split(",") if "[::1]" not in h and "::1" not in h])
        os.environ[env_key] = cleaned

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Role-Based AI Candidate Screening System"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Storage & Persistence
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/data/screening.db"
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "data" / "chroma_db")
    CORPUS_DIR: str = str(BASE_DIR / "data" / "corpus")
    SAMPLE_RESUMES_DIR: str = str(BASE_DIR / "data" / "sample_resumes")
    UPLOAD_DIR: str = str(BASE_DIR / "data" / "uploads")
    
    # LLM Settings
    LLM_PROVIDER: str = "auto"  # 'openai', 'gemini', 'auto', or 'local'
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Interview Config
    QUESTIONS_PER_SESSION: int = 5
    CHUNK_SIZE: int = 700
    CHUNK_OVERLAP: int = 100
    RAG_TOP_K: int = 3
    
    # CORS
    CORS_ORIGINS: list[str] = ["*"]
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure necessary data directories exist
os.makedirs(os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
os.makedirs(settings.CORPUS_DIR, exist_ok=True)
os.makedirs(settings.SAMPLE_RESUMES_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
