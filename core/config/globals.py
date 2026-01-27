from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # JWT Configuration
    JWT_KEY: str = "396d399d8f19cb5b4ad13b25187449b0c0e7447cf4b06545a7b9a75e8f7cf20c"
    JWT_ALG: str = "HS256"

    # Database Configuration
    DB_NAME: str = "postgres"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "example"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_DRIVER: str = "postgres"

    # Application Mode
    MODE: str = "PROD"

    # Owner Configuration
    OWNER_USER: str = "admin"
    OWNER_PASS: str = "change_this_password"
    OWNER_EMAIL: str = "example@example.com"

    # Observer Configuration
    OBSERVER_USER: str = "observer"
    OBSERVER_PASS: str = "observer"
    OBSERVER_EMAIL: str = "observer@admin.com"

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # AI Configuration (Optional)
    OPENAI_API_KEY: str = "sk-..."
    ANTHROPIC_API_KEY: str = "sk-ant-..."
    IA_MODEL_NAME: str = "gpt-4-turbo-preview"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Singleton Instance
settings = Settings()
