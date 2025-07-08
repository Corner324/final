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


DATABASE_URL: str | None = os.getenv("ADMIN_DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("ADMIN_DATABASE_URL environment variable must be set")

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class BasicAuthBackend(AuthenticationBackend):
    """Простейшая Basic-auth аутентификация."""

    def __init__(self) -> None:
        secret = os.getenv("ADMIN_SECRET_KEY", "change-me-please")
        super().__init__(secret_key=secret)

    async def authenticate(self, request: Request):  # type: ignore[override]
        import base64, os

        if user := request.session.get("user"):
            return AuthCredentials(["authenticated"]), SimpleUser(user)

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
        User.team,
        User.created_at,
    ]

    form_excluded_columns = [
        "hashed_password",
        "created_at",
        "updated_at",
    ]

    async def scaffold_form(self) -> type:
        """Создает форму с дополнительным полем пароля."""
        form_class = await super().scaffold_form()

        form_class.password = PasswordField("Password")

        return form_class

    page_size = 50
    name = "User"
    name_plural = "Users"

    async def on_model_change(self, form, model, is_created, request):  # type: ignore[override]
        """Хэшируем пароль при создании/обновлении пользователя."""

        print(f"DEBUG: form type: {type(form)}")
        print(f"DEBUG: form content: {form}")

        password: str | None = form.get("password") if isinstance(form, dict) else None

        print(f"DEBUG: extracted password: {password}")
        print(f"DEBUG: is_created: {is_created}")

        if is_created:
            if not password:
                raise ValueError("Пароль обязателен при создании пользователя")
            model.hashed_password = _hash_password(password)
            if model.role is None:
                model.role = "user"
        else:
            if password:
                model.hashed_password = _hash_password(password)


admin.add_view(TeamAdmin)
admin.add_view(UserAdmin)


# Health-check
@app.get("/")
async def root() -> dict[str, str]:
    """Простое сообщение, подтверждающее работу сервиса."""

    return {"msg": "admin panel service"}
