from pydantic import BaseModel
from datetime import datetime


class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    code: str


class TeamUpdate(TeamBase):
    pass


class TeamOut(TeamBase):
    id: int
    code: str
    created_at: datetime

    class Config:
        from_attributes = True
