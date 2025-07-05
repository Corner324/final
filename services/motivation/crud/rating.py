from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import Rating
from schemas import RatingCreate, AverageScores


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


async def create_rating(db: AsyncSession, data: RatingCreate) -> Rating:
    obj = Rating(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_user_ratings(db: AsyncSession, user_id: int) -> list[Rating]:
    res = await db.execute(select(Rating).where(Rating.user_id == user_id))
    return res.scalars().all()


async def get_team_ratings(db: AsyncSession, team_id: int) -> list[Rating]:
    res = await db.execute(select(Rating).where(Rating.team_id == team_id))
    return res.scalars().all()


# ---------------------------------------------------------------------------
# Aggregations
# ---------------------------------------------------------------------------


def _row_to_avg(row) -> AverageScores:
    return AverageScores(timeliness=row[0], completeness=row[1], quality=row[2])


async def get_user_average(
    db: AsyncSession, user_id: int, period_days: int | None = None
) -> AverageScores:
    stmt = select(
        func.avg(Rating.timeliness_score),
        func.avg(Rating.completeness_score),
        func.avg(Rating.quality_score),
    ).where(Rating.user_id == user_id)
    if period_days is not None:
        cutoff = datetime.utcnow() - timedelta(days=period_days)
        stmt = stmt.where(Rating.created_at >= cutoff)
    res = await db.execute(stmt)
    row = res.first()
    return _row_to_avg(row) if row else AverageScores()


async def get_team_average(
    db: AsyncSession, team_id: int, period_days: int | None = None
) -> AverageScores:
    stmt = select(
        func.avg(Rating.timeliness_score),
        func.avg(Rating.completeness_score),
        func.avg(Rating.quality_score),
    ).where(Rating.team_id == team_id)
    if period_days is not None:
        cutoff = datetime.utcnow() - timedelta(days=period_days)
        stmt = stmt.where(Rating.created_at >= cutoff)
    res = await db.execute(stmt)
    row = res.first()
    return _row_to_avg(row) if row else AverageScores()
