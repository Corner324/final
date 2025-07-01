from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models import Motivation
from schemas import MotivationCreate


async def create_motivation(db: AsyncSession, data: MotivationCreate) -> Motivation:
    motivation = Motivation(**data.model_dump())
    db.add(motivation)
    await db.commit()
    await db.refresh(motivation)
    return motivation


async def get_motivation(db: AsyncSession, motivation_id: int) -> Motivation | None:
    result = await db.execute(select(Motivation).where(Motivation.id == motivation_id))
    return result.scalar_one_or_none()


async def get_all_motivations(db: AsyncSession) -> list[Motivation]:
    result = await db.execute(select(Motivation).order_by(Motivation.created_at.desc()))
    return result.scalars().all()


async def delete_motivation(db: AsyncSession, motivation_id: int) -> None:
    await db.execute(delete(Motivation).where(Motivation.id == motivation_id))
    await db.commit()
