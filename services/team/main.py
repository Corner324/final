import json
from fastapi import FastAPI, Request
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from routers import routers
from core.config import get_settings
from deps.db import SessionLocal
from models.user import User, UserStatus, UserRole
from sqlalchemy import select
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
from faststream.rabbit.fastapi import RabbitRouter


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f">> {request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"<< {response.status_code} {request.url.path}")
        return response


app = FastAPI()
app.add_middleware(LoggingMiddleware)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc):  # type: ignore[override]
    return JSONResponse(
        status_code=400,
        content={"detail": "Запись с такими уникальными данными уже существует"},
    )


for router in routers:
    app.include_router(router)


settings = get_settings()

rabbit_router = RabbitRouter(settings.rabbit_url or "amqp://guest:guest@rabbitmq/")


@rabbit_router.subscriber(
    "user.events", queue="user.events.team", exchange_type="fanout"
)
async def handle_user_event(body: dict):
    logger.info(f"Received event: {body.get('event')}")
    if body.get("event") == "created":
        await _sync_user(body["payload"])


app.include_router(rabbit_router)


async def _sync_user(payload: dict):
    """Создать или обновить пользователя в локальной БД team."""

    status = payload.get("status", "active")
    if status == "inactive":
        status = "active"
    role = payload.get("role", "user")
    if role == "superadmin":
        role = "admin"

    async with SessionLocal() as db:
        res = await db.execute(select(User).where(User.id == payload["id"]))
        user: User | None = res.scalar_one_or_none()
        if not user:
            user = User(
                id=payload["id"],
                email=payload["email"],
                hashed_password=payload["hashed_password"],
                full_name=payload.get("full_name"),
                status=UserStatus(status),
                role=UserRole(role),
                team_id=payload.get("team_id"),
                is_active=payload.get("is_active", True),
                is_admin=payload.get("is_admin", False),
            )
            db.add(user)
            logger.info(f"User synced (created) id={user.id}")
        else:
            user.email = payload["email"]
            user.full_name = payload.get("full_name")
            user.status = UserStatus(status)
            user.role = UserRole(role)
            user.team_id = payload.get("team_id")
            user.is_active = payload.get("is_active", True)
            user.is_admin = payload.get("is_admin", False)
        await db.commit()
        if user:
            logger.debug(f"User upsert completed id={user.id}")
