from fastapi import FastAPI
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from starlette.middleware.cors import CORSMiddleware
import os
from routers import user, auth
from routers import admin
from models.user import User
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse

DATABASE_URL = os.getenv("DATABASE_URL")

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)

app = FastAPI(title="Auth Service", version="0.1.0")


# ---------------------------------------------------------------------------
# Global error handlers
# ---------------------------------------------------------------------------


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc):  # type: ignore[override]
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
