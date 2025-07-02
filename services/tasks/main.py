from fastapi import FastAPI
from faststream.rabbit.fastapi import RabbitRouter
import os
from routers import tasks

rabbit_router = RabbitRouter(os.getenv("RABBIT_URL"))

app = FastAPI()
app.include_router(tasks.router)
app.include_router(rabbit_router)
