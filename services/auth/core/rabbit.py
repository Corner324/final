import json
from loguru import logger
from faststream.rabbit.fastapi import RabbitRouter
from core.config import get_settings


settings = get_settings()

# Инициализируем общий RabbitRouter для FastAPI-интеграции
rabbit_router = RabbitRouter(settings.rabbit_url)

EXCHANGE_NAME = "user.events"


async def publish_user_event(event: str, payload: dict) -> None:
    """Публикуем событие пользователя через FastStream Rabbit broker."""

    logger.info(f"Publish user event '{event}' to exchange '{EXCHANGE_NAME}'")
    await rabbit_router.broker.publish(
        {"event": event, "payload": payload},
        EXCHANGE_NAME,
        exchange_type="fanout",
    )
    logger.debug(f"Message sent: {payload}")
