from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from models.team import Team
from schemas.team import TeamCreate


async def get_team_by_code(db: AsyncSession, code: str) -> Team | None:
    result = await db.execute(select(Team).where(Team.code == code))
    return result.scalar_one_or_none()


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
