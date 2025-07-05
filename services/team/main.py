from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from routers import routers

app = FastAPI()


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc):  # type: ignore[override]
    return JSONResponse(
        status_code=400,
        content={"detail": "Запись с такими уникальными данными уже существует"},
    )


for router in routers:
    app.include_router(router)


# Заглушка для запуска
@app.get("/")
def root():
    return {"msg": "team service"}
