from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    rabbit_url: str = "amqp://guest:guest@rabbitmq/"
    # По умолчанию токен живёт час, чтобы было проще отлаживать клиент
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"
    postgres_db: str
    postgres_user: str
    postgres_password: str

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
