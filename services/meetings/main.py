from fastapi import FastAPI
from faststream.rabbit.fastapi import RabbitRouter
import os
from routers import meetings

rabbit_router = RabbitRouter(os.getenv("RABBIT_URL"))

app = FastAPI()
app.include_router(meetings.router)
app.include_router(rabbit_router)
