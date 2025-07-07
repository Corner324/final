import json
import aio_pika
from loguru import logger
from core.config import get_settings

settings = get_settings()

RABBIT_URL = settings.rabbit_url
EXCHANGE_NAME = "user.events"


async def publish_user_event(event: str, payload: dict) -> None:
    """Publish user event to RabbitMQ (fanout exchange)."""
    logger.info(f"Publish user event '{event}' to exchange '{EXCHANGE_NAME}'")
    connection = await aio_pika.connect_robust(RABBIT_URL)
    try:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            EXCHANGE_NAME, aio_pika.ExchangeType.FANOUT, durable=True
        )
        message = aio_pika.Message(
            body=json.dumps({"event": event, "payload": payload}).encode()
        )
        await exchange.publish(message, routing_key="")
        logger.debug(f"Message sent: {payload}")
    finally:
        await connection.close()
