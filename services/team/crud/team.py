from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from models.team import Team
from schemas.team import TeamCreate, TeamUpdate
from typing import List


async def create_team(db: AsyncSession, team_in: TeamCreate) -> Team:
    db_team = Team(name=team_in.name, code=team_in.code)
    db.add(db_team)
    try:
        await db.commit()
        await db.refresh(db_team)
    except IntegrityError:
        await db.rollback()
        raise
    return db_team


async def get_team_by_id(db: AsyncSession, team_id: int) -> Team | None:
    result = await db.execute(select(Team).where(Team.id == team_id))
    return result.scalar_one_or_none()


async def get_team_by_code(db: AsyncSession, code: str) -> Team | None:
    result = await db.execute(select(Team).where(Team.code == code))
    return result.scalar_one_or_none()


async def get_teams(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Team]:
    result = await db.execute(select(Team).offset(skip).limit(limit))
    return result.scalars().all()


async def update_team(db: AsyncSession, db_team: Team, team_in: TeamUpdate) -> Team:
    db_team.name = team_in.name
    await db.commit()
    await db.refresh(db_team)
    return db_team


async def delete_team(db: AsyncSession, db_team: Team) -> None:
    await db.delete(db_team)
    await db.commit()
