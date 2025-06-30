from fastapi import FastAPI
from routers import team

app = FastAPI()

app.include_router(team.router)


# Заглушка для запуска
@app.get("/")
def root():
    return {"msg": "team service"}
