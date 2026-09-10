from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated application configuration loaded from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "SentinelPay Fraud Intelligence API"
    app_version: str = "1.0.0"
    environment: Literal["local", "test", "production"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    database_url: SecretStr = SecretStr(
        "postgresql+asyncpg://sentinelpay:sentinelpay@localhost:5432/sentinelpay"
    )
    redis_url: SecretStr = SecretStr("redis://:sentinelpay@localhost:6379/0")
    api_key: SecretStr = SecretStr("local-development-key")
    persistence_enabled: bool = True
    api_key_required: bool = False
    model_path: str = "artifacts/fraud_model.joblib"
    dashboard_enabled: bool = True


@lru_cache
def get_settings() -> Settings:
    """Return one cached and validated settings instance."""

    return Settings()

