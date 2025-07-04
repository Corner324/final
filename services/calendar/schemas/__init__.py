from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CalendarEventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    owner_id: int
    is_team_event: bool = False


class CalendarEventCreate(CalendarEventBase):
    pass


class CalendarEventRead(CalendarEventBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
