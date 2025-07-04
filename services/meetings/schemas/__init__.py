from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional


class MeetingBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    team_id: int
    participants: List[int] = Field(default_factory=list)

    @validator("end_time")
    def validate_time(cls, v, values):
        if "start_time" in values and v <= values["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class MeetingCreate(MeetingBase):
    organizer_id: int


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    participants: Optional[List[int]] = None


class MeetingOut(MeetingBase):
    id: int
    organizer_id: int
    created_at: datetime

    class Config:
        from_attributes = True
