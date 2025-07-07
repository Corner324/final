import os
import sys
from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.team import Base


context.config.set_main_option("script_location", os.path.dirname(__file__))
from models import user, news  # noqa: F401

ASYNC_DATABASE_URL = os.environ.get("DATABASE_URL")
if not ASYNC_DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment variables!")

SYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("+asyncpg", "+psycopg2")

config = context.config
config.set_main_option("sqlalchemy.url", str(SYNC_DATABASE_URL))

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=SYNC_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_engine(SYNC_DATABASE_URL, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
