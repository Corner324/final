from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NewsBase(BaseModel):
    title: str
    content: str
    team_id: int
    author_id: int


class NewsCreate(NewsBase):
    pass


class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class NewsOut(NewsBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
