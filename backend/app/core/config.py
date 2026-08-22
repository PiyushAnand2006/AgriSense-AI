"""Application settings loaded from environment variables / .env file."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database. Defaults to a local SQLite file so the project runs with zero
    # infrastructure; docker-compose / production point this at PostgreSQL.
    database_url: str = f"sqlite:///{(BACKEND_DIR / 'agrisense.db').as_posix()}"

    # Auth
    jwt_secret: str = "dev-only-insecure-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_days: int = 7

    # CORS (comma separated origins)
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Uploads
    upload_dir: str = "uploads"
    max_upload_mb: int = 8

    # --- External API integrations (all optional; DB fallbacks apply) -------

    # Open-Meteo-compatible forecast endpoint (no key needed by default).
    weather_api_url: str = "https://api.open-meteo.com/v1"
    weather_api_key: str = ""

    # AGMARKNET-style mandi price feed. When empty, market data is served
    # from the local database (source: "mandi-db").
    mandi_api_url: str = ""
    mandi_api_key: str = ""

    # External conversational API for the farmer assistant. When empty the
    # built-in rule-based assistant answers.
    assistant_api_url: str = ""
    assistant_api_key: str = ""

    # --- Caching / rate limiting ----------------------------------------------

    # Redis connection for shared caching. When empty (or the optional redis
    # package is missing) a process-local TTL cache is used instead.
    redis_url: str = ""

    # Simple fixed-window rate limits (requests per minute per IP).
    rate_limit_auth: int = 30
    rate_limit_assistant: int = 20
    rate_limit_uploads: int = 30

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def upload_path(self) -> Path:
        path = BACKEND_DIR / self.upload_dir
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def weather_integration_active(self) -> bool:
        return bool(self.weather_api_url)

    @property
    def mandi_integration_active(self) -> bool:
        return bool(self.mandi_api_url)

    @property
    def assistant_integration_active(self) -> bool:
        return bool(self.assistant_api_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()
