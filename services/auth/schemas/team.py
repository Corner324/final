from pydantic import BaseModel
from typing import Optional


class TeamBase(BaseModel):
    name: str
    code: str


class TeamCreate(TeamBase):
    pass


class TeamOut(TeamBase):
    id: int

    class Config:
        from_attributes = True
