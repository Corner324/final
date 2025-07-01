from fastapi import FastAPI
from routers import motivation

app = FastAPI()
app.include_router(motivation.router)
