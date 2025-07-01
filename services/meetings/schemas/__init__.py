from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MeetingBase(BaseModel):
    title: str
    description: Optional[str] = None
    scheduled_at: datetime


class MeetingCreate(MeetingBase):
    pass


class MeetingRead(MeetingBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
