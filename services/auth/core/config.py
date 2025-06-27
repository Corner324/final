from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    postgres_db: str
    postgres_user: str
    postgres_password: str

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
