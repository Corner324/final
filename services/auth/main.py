from fastapi import FastAPI, Request
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from starlette.middleware.cors import CORSMiddleware
import os
from routers import user, auth
from routers import admin
from models.user import User
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from core.rabbit import rabbit_router

DATABASE_URL = os.getenv("DATABASE_URL")

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f">> {request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"<< {response.status_code} {request.url.path}")
        return response


async def lifespan(app: FastAPI):
    logger.info("Auth service started.")
    yield
    await engine.dispose()
    logger.info("Auth service stopped.")


app = FastAPI(title="Auth Service", version="0.1.0", lifespan=lifespan)
app.add_middleware(LoggingMiddleware)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc):
    """Возвращаем 400 при нарушении уникальных ограничений."""

    return JSONResponse(
        status_code=400,
        content={"detail": "Запись с такими уникальными данными уже существует"},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(rabbit_router)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
