from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    app_env: str

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: int

    database_url: str

    redis_host: str
    redis_port: int
    redis_db: int

    mistral_api_key: str

    celery_broker_url: str

    timezone: str = "Asia/Karachi"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()