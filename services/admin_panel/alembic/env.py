import os
import sys
from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from alembic import context

# Автоматически подгружаем переменные из .env
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Добавляем корень микросервиса в PYTHONPATH для корректного импорта models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models import Base

# Явно указываем script_location для Alembic
context.config.set_main_option("script_location", os.path.dirname(__file__))

# Берём URL из переменной ADMIN_DATABASE_URL либо DATABASE_URL
ASYNC_DATABASE_URL = os.environ.get("ADMIN_DATABASE_URL") or os.environ.get(
    "DATABASE_URL"
)
if not ASYNC_DATABASE_URL:
    raise RuntimeError("ADMIN_DATABASE_URL не задана в переменных окружения!")
# Для миграций используем sync-URL
SYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("+asyncpg", "+psycopg2")

config = context.config
# Прописываем URL в конфиг
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
