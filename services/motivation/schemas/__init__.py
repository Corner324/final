from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MotivationBase(BaseModel):
    title: str
    description: Optional[str] = None


class MotivationCreate(MotivationBase):
    pass


class MotivationRead(MotivationBase):
    id: int
    created_at: datetime
