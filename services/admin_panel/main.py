import os

from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.authentication import AuthCredentials, SimpleUser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from wtforms import PasswordField
from passlib.context import CryptContext

from models import Base, Team, User

# Конфигурация БД


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
# Basic HTTP Auth для входа в админ-панель
# ---------------------------------------------------------------------------


class BasicAuthBackend(AuthenticationBackend):
    """Простейшая Basic-auth аутентификация."""

    def __init__(self) -> None:
        # SQLAdmin требует секрет для подписи cookie сессии
        secret = os.getenv("ADMIN_SECRET_KEY", "change-me-please")
        super().__init__(secret_key=secret)

    async def authenticate(self, request: Request):  # type: ignore[override]
        import base64, os

        # 1. Проверяем сессию (устанавливается методом login)
        if user := request.session.get("user"):
            return AuthCredentials(["authenticated"]), SimpleUser(user)

        # 2. Fallback: Basic-Auth заголовок (подходит для API-клиентов)
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        scheme, _, credentials = auth_header.partition(" ")
        if scheme.lower() != "basic" or not credentials:
            return None

        try:
            username, _, password = (
                base64.b64decode(credentials).decode().partition(":")
            )
        except Exception:
            return None

        if username == os.getenv("ADMIN_USER") and password == os.getenv("ADMIN_PASS"):
            return AuthCredentials(["authenticated"]), SimpleUser(username)
        return None

    async def login(self, request: Request):  # type: ignore[override]
        """Обработка формы /admin/login. Проверяем username/password."""

        form = await request.form()
        username = form.get("username") if form else None
        password = form.get("password") if form else None
        if username == os.getenv("ADMIN_USER") and password == os.getenv("ADMIN_PASS"):
            request.session.update({"user": username})
            return True
        return False

    async def logout(self, request: Request):  # type: ignore[override]
        """Очищаем сессию (SQLAdmin делает это сам)."""

        request.session.pop("user", None)
        return True


# ---------------------------------------------------------------------------
# Приложение FastAPI + SQLAdmin
# ---------------------------------------------------------------------------

app = FastAPI(title="Admin Panel Service")
admin = Admin(
    app,
    engine,
    session_maker=SessionLocal,
    authentication_backend=BasicAuthBackend(),
)

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
        User.team,  # показываем связанную команду
        User.created_at,
    ]

    # Exclude hashed password but показываем team
    form_excluded_columns = [
        "hashed_password",
        "created_at",
        "updated_at",
    ]

    async def scaffold_form(self) -> type:
        """Создает форму с дополнительным полем пароля."""
        form_class = await super().scaffold_form()

        # Добавляем поле пароля
        form_class.password = PasswordField("Password")

        return form_class

    page_size = 50
    name = "User"
    name_plural = "Users"

    async def on_model_change(self, form, model, is_created, request):  # type: ignore[override]
        """Хэшируем пароль при создании/обновлении пользователя."""

        # form - это словарь, а не объект WTForms!
        print(f"DEBUG: form type: {type(form)}")
        print(f"DEBUG: form content: {form}")

        # Получаем пароль из словаря
        password: str | None = form.get("password") if isinstance(form, dict) else None

        print(f"DEBUG: extracted password: {password}")
        print(f"DEBUG: is_created: {is_created}")

        # При создании пароль обязателен
        if is_created:
            if not password:
                raise ValueError("Пароль обязателен при создании пользователя")
            model.hashed_password = _hash_password(password)
            # Выставляем роль по-умолчанию
            if model.role is None:
                model.role = "user"
        else:
            # При редактировании пароль опционален
            if password:
                model.hashed_password = _hash_password(password)


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
