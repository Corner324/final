from fastapi import FastAPI
from routers import meetings

app = FastAPI()
app.include_router(meetings.router)
