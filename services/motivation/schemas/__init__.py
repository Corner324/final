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


# Rating schemas



class RatingBase(BaseModel):
    user_id: int
    task_id: int
    reviewer_id: int
    team_id: int
    timeliness_score: int
    completeness_score: int
    quality_score: int


class RatingCreate(RatingBase):
    pass


class RatingRead(RatingBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Matrix / Average responses
# ---------------------------------------------------------------------------


class AverageScores(BaseModel):
    timeliness: float | None = None
    completeness: float | None = None
    quality: float | None = None


class UserMatrixResponse(BaseModel):
    ratings: list[RatingRead]
    average_quarter: AverageScores
    average_all: AverageScores


class TeamAverageResponse(BaseModel):
    team_id: int
    average: AverageScores
