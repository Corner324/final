import asyncio, json
from fastapi import FastAPI, Request
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from routers import routers
from core.config import get_settings
from deps.db import SessionLocal
from models.user import User, UserStatus, UserRole
from sqlalchemy import select
import aio_pika
import contextlib
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger


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


# Заглушка для запуска
@app.get("/")
def root():
    return {"msg": "team service"}


# --- RabbitMQ consumer для синхронизации пользователей ---


async def _sync_user(payload: dict):
    """Создать или обновить пользователя в локальной БД team."""
    # Приведение значений к Enumам team
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


async def _consume_user_events():
    settings = get_settings()
    logger.info("Starting RabbitMQ consumer for user.events")
    connection = await aio_pika.connect_robust(
        settings.rabbit_url or "amqp://guest:guest@rabbitmq/"
    )
    channel = await connection.channel()
    exchange = await channel.declare_exchange(
        "user.events", aio_pika.ExchangeType.FANOUT, durable=True
    )
    queue = await channel.declare_queue("user.events.team", durable=True)
    await queue.bind(exchange)

    async with queue.iterator() as q_iter:
        async for message in q_iter:
            async with message.process():
                data = json.loads(message.body)
                logger.info(f"Received event: {data.get('event')}")
                if data.get("event") == "created":
                    await _sync_user(data["payload"])


@app.on_event("startup")
async def _start_consumer():
    logger.info("Team service startup")
    app.state.user_consumer_task = asyncio.create_task(_consume_user_events())


@app.on_event("shutdown")
async def _stop_consumer():
    task: asyncio.Task = app.state.user_consumer_task  # type: ignore[attr-defined]
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task
    logger.info("Team service shutdown")
