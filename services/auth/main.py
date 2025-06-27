from fastapi import FastAPI
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from starlette.middleware.cors import CORSMiddleware
import os
from routers import user, auth
from models.user import User
from models.team import Team

DATABASE_URL = os.getenv("DATABASE_URL")

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)

app = FastAPI(title="Auth Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)


@app.on_event("startup")
async def startup():
    logger.info("Auth service started.")


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
    logger.info("Auth service stopped.")


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
