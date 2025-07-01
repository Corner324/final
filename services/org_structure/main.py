from fastapi import FastAPI
from routers import org_structure

app = FastAPI()
app.include_router(org_structure.router)
