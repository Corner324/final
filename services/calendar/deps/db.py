from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from fastapi import Depends
from models import Base
import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/calendar"
)

engine = create_async_engine(DATABASE_URL, future=True, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


class Settings(BaseSettings):
    database_url: str
    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )
