import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl, PostgresDsn

class Settings(BaseSettings):
    DATABASE_URL: str
    CELERY_DATABASE_URL: str
    REDIS_URL: str
    ANTHROPIC_API_KEY: str
    CLERK_SECRET_KEY: str
    CLERK_PUBLISHABLE_KEY: str
    R2_ACCOUNT_ID: str
    R2_ACCESS_KEY_ID: str
    R2_SECRET_ACCESS_KEY: str
    R2_BUCKET_NAME: str
    R2_PUBLIC_URL: str
    LANGSMITH_API_KEY: str | None = None
    LANGSMITH_PROJECT: str | None = None
    SENTRY_DSN: str | None = None
    LOGFIRE_TOKEN: str | None = None
    OLLAMA_BASE_URL: str | None = None
    OLLAMA_MODEL: str | None = None
    EMBEDDING_MODEL_PATH: str
    EMBEDDING_MODEL_VERSION: str
    MAX_BATCH_FILES: int
    MAX_FILE_SIZE_MB: int
    AUTO_REJECT_THRESHOLD: float
    AUTO_SHORTLIST_THRESHOLD: float = 75.0
    JWT_CACHE_TTL_SECONDS: int
    ENVIRONMENT: str
    SECRET_KEY: str
    LANGCHAIN_TRACING_V2: str | None = None
    ENABLE_LANGGRAPH_CHECKPOINTS: bool = True
    JOB_EMBEDDING_CACHE_TTL_SECONDS: int = 3600
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str | None = None
    SMTP_USE_TLS: bool = True

    model_config = SettingsConfigDict(env_file=".env.local", extra="ignore")

settings = Settings()
