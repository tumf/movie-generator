"""Configuration settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # PocketBase
    pocketbase_url: str = "http://localhost:8090"

    # Rate limiting
    max_queue_size: int = 10
    rate_limit_per_day: int = 5
    max_video_duration_minutes: int = 5

    # Job expiration
    job_expiration_hours: int = 24

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000


settings = Settings()
