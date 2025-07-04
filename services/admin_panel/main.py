import os

from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from wtforms import PasswordField
from passlib.context import CryptContext

from models import Base, Team, User

# ---------------------------------------------------------------------------
# Конфигурация БД
# ---------------------------------------------------------------------------

DATABASE_URL: str = os.getenv(
    "ADMIN_DATABASE_URL",
    # По умолчанию используем SQLite для упрощённого локального запуска
    "sqlite:///./admin_panel.db",
)

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Создаём таблицы, если их ещё нет
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# Приложение FastAPI + SQLAdmin
# ---------------------------------------------------------------------------

app = FastAPI(title="Admin Panel Service")
admin = Admin(app, engine, session_maker=SessionLocal)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_password(password: str) -> str:
    """Return hashed representation of plain password."""

    return pwd_context.hash(password)


class TeamAdmin(ModelView, model=Team):
    # Отображаемые колонки
    column_list = [Team.id, Team.name, Team.code, Team.created_at]
    page_size = 50
    name = "Team"
    name_plural = "Teams"


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.email,
        User.full_name,
        User.role,
        User.status,
        User.is_active,
        User.team_id,
        User.created_at,
    ]

    # Поля, которые НЕ показываем в форме
    form_excluded_columns = [
        "hashed_password",
        "is_admin",
        "created_at",
        "updated_at",
    ]

    # Дополнительное поле «пароль» (plain-text) для формы создания/редактирования
    form_extra_fields = {"password": PasswordField("Password")}

    page_size = 50
    name = "User"
    name_plural = "Users"

    def on_model_change(self, form, model, is_created):  # type: ignore[override]
        """Хэшируем пароль при создании/обновлении пользователя."""

        password: str | None = form.password.data if hasattr(form, "password") else None  # type: ignore[attr-defined]
        if password:
            model.hashed_password = _hash_password(password)

        # При создании не забываем выставить роль по-умолчанию
        if is_created and model.role is None:
            model.role = "user"


# Регистрируем модели в админке
admin.add_view(TeamAdmin)
admin.add_view(UserAdmin)


# ---------------------------------------------------------------------------
# Health-check / заглушка для запуска
# ---------------------------------------------------------------------------


@app.get("/")
async def root() -> dict[str, str]:
    """Простое сообщение, подтверждающее работу сервиса."""

    return {"msg": "admin panel service"}
