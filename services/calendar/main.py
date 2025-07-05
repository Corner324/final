from fastapi import FastAPI
from faststream.rabbit.fastapi import RabbitRouter
from routers import router as calendar_router
import os

rabbit_router = RabbitRouter(os.getenv("RABBIT_URL"))

app = FastAPI(title="Calendar Service", version="0.1.0")
app.include_router(calendar_router)
app.include_router(rabbit_router)


@rabbit_router.subscriber("motivation_events")
async def handle_motivation_event(body: dict):
    print("Получено событие из motivation:", body)
    # ... твоя логика обработки события ...
