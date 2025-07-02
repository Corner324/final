from fastapi import FastAPI
from faststream.rabbit.fastapi import RabbitRouter
import os
from routers import org_structure

rabbit_router = RabbitRouter(os.getenv("RABBIT_URL"))

app = FastAPI()
app.include_router(org_structure.router)
app.include_router(rabbit_router)
