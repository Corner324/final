import os
import sys
from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from alembic import context
from glob import glob
from importlib import import_module

# Явно указываем script_location для Alembic
context.config.set_main_option("script_location", os.path.dirname(__file__))

# Автоматически подгружаем переменные из .env
try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass

# Добавляем корень микросервиса в PYTHONPATH для корректного импорта models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Универсальный импорт Base из всех моделей
base_list = []
# Добавляем models/__init__.py
init_model_file = os.path.join(os.path.dirname(__file__), "..", "models", "__init__.py")
if os.path.exists(init_model_file):
    try:
        mod = import_module("models")
        if hasattr(mod, "Base"):
            base_list.append(getattr(mod, "Base"))
    except Exception:
        pass
models_path = os.path.join(os.path.dirname(__file__), "..", "models", "*.py")
for model_file in glob(models_path):
    module_name = f"models.{os.path.splitext(os.path.basename(model_file))[0]}"
    if module_name.endswith("__init__"):
        continue
    try:
        mod = import_module(module_name)
        if hasattr(mod, "Base"):
            base_list.append(getattr(mod, "Base"))
    except Exception:
        pass

if not base_list:
    raise RuntimeError("Не найден ни один Base в models! Проверьте структуру моделей.")

# Если несколько Base, берем metadata первого (или объединяем, если нужно)
target_metadata = base_list[0].metadata

ASYNC_DATABASE_URL = os.environ.get("DATABASE_URL")
if not ASYNC_DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment variables!")
# Для миграций используем sync-URL
SYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("+asyncpg", "+psycopg2")

config = context.config
config.set_main_option("sqlalchemy.url", str(SYNC_DATABASE_URL))


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
