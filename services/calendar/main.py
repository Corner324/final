from fastapi import FastAPI
from faststream.rabbit.fastapi import RabbitRouter
import os

rabbit_router = RabbitRouter(os.getenv("RABBIT_URL"))

app = FastAPI()
app.include_router(rabbit_router)


@rabbit_router.subscriber("motivation_events")
async def handle_motivation_event(body: dict):
    print("Получено событие из motivation:", body)
    # ... твоя логика обработки события ...
