from fastapi import FastAPI
from faststream.rabbit.fastapi import RabbitBroker, RabbitRouter
import os
from routers import motivation


rabbit_router = RabbitRouter(os.getenv("RABBIT_URL"))

def broker():
    return router.broker

app = FastAPI()
app.include_router(motivation.router)
app.include_router(rabbit_router)
