from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import ConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str = "team_secret"
    rabbit_url: str | None = None

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
