"""Application settings loaded from environment variables."""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application configuration."""

    # Application
    APP_NAME: str = "ShreeGlassFiber"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    BASE_URL: str = "http://localhost:8000"
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    JWT_SECRET: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "shreeglass"
    DATABASE_URL: str = ""
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Super Admin
    SUPER_ADMIN_EMAIL: str = "admin@shreeglass.com"
    SUPER_ADMIN_PASSWORD: str = "SuperAdmin@123"

    # Upload
    UPLOAD_PATH: str = "uploads"
    MAX_IMAGE_SIZE_MB: int = 5
    MAX_PDF_SIZE_MB: int = 20

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = ""

    # App Version Control
    ANDROID_MIN_VERSION: str = "1.0.0"
    IOS_MIN_VERSION: str = "1.0.0"
    FORCE_UPDATE: bool = False
    MAINTENANCE_MODE: bool = False

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def build_database_url(cls, value, info):
        if value:
            return value

        data = info.data
        user = data.get("POSTGRES_USER", "postgres")
        password = data.get("POSTGRES_PASSWORD", "postgres")
        host = data.get("POSTGRES_HOST", "localhost")
        port = data.get("POSTGRES_PORT", 5432)
        db = data.get("POSTGRES_DB", "shreeglass")
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
