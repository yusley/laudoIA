from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "LaudoIA Pericial API"
    APP_ENV: str = "development"
    APP_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ADMIN_EMAILS: str = "yusley.santos23@gmail.com"
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/laudoia"
    UPLOAD_DIR: str = "storage/uploads"
    REPORT_TEMPLATE_PATH: str = "app/assets/report_template.docx"
    MERCADO_PAGO_ACCESS_TOKEN: str = ""
    MERCADO_PAGO_WEBHOOK_URL: str = "http://localhost:8000/api/v1/billing/webhooks/mercado-pago"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_DEFAULT_MODEL: str = "openrouter/owl-alpha"
    OPENROUTER_VISION_MODEL: str = "openai/gpt-4o-mini"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_REQUEST_TIMEOUT_SECONDS: int = 25
    OPENROUTER_FREE_MODEL_MAX_ATTEMPTS: int = 1
    USD_BRL_RATE: float = 5.20
    CREDIT_VALUE_BRL: float = 1.00
    PLATFORM_MARGIN_MULTIPLIER: float = 1.35

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
