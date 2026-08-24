"""
Application configuration.

All runtime configuration is loaded from environment variables (see
.env.example at the project root) via pydantic-settings. Never hardcode
secrets here — this module only defines shape, types, and defaults.
"""
from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- App ----
    APP_NAME: str = "AskMyDocs AI"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: str = "http://localhost:3000"

    # ---- Database ----
    DATABASE_URL: str = "postgresql+asyncpg://askmydocs:change_me@db:5432/askmydocs"

    # ---- Redis ----
    REDIS_URL: str = "redis://redis:6379/0"

    # ---- Auth ----
    JWT_SECRET_KEY: str = "insecure-dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ---- LLM ----
    LLM_PROVIDER: str = "ollama"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3.1"

    # ---- Groq (OpenAI-compatible, fast hosted inference) ----
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    # ---- Cohere (hosted reranking, avoids loading a local cross-encoder) ----
    COHERE_API_KEY: str = ""

    # ---- Embeddings ----
    EMBEDDING_PROVIDER: str = "huggingface"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CROSS_ENCODER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # ---- Vector store ----
    VECTOR_STORE_PATH: str = "./storage/vector_store"
    FAISS_INDEX_NAME: str = "askmydocs_index"

    # ---- File storage ----
    UPLOAD_DIR: str = "./storage/uploads"
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_FILE_TYPES: str = ".pdf,.docx,.txt,.md"

    # ---- Retrieval ----
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 120
    BM25_TOP_K: int = 20
    VECTOR_TOP_K: int = 20
    RRF_K: int = 60
    RERANK_TOP_K: int = 5
    MIN_CONFIDENCE_SCORE: float = 0.35

    # ---- Evaluation ----
    RAGAS_ENABLED: bool = True
    DEEPEVAL_ENABLED: bool = True

    # ---- Logging ----
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    @field_validator("CORS_ORIGINS")
    @classmethod
    def _validate_cors(cls, v: str) -> str:
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def allowed_file_types_list(self) -> List[str]:
        return [ext.strip().lower() for ext in self.ALLOWED_FILE_TYPES.split(",") if ext.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton — avoids re-parsing env on every import."""
    return Settings()


settings = get_settings()
