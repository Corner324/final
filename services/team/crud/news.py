from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.news import News
from schemas.news import NewsCreate, NewsUpdate


async def create_news(db: AsyncSession, data: NewsCreate) -> News:
    obj = News(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_news_item(db: AsyncSession, news_id: int) -> News | None:
    res = await db.execute(select(News).where(News.id == news_id))
    return res.scalar_one_or_none()


async def get_team_news(db: AsyncSession, team_id: int) -> list[News]:
    res = await db.execute(
        select(News).where(News.team_id == team_id).order_by(News.created_at.desc())
    )
    return res.scalars().all()


async def update_news_item(db: AsyncSession, obj: News, data: NewsUpdate) -> News:
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_news_item(db: AsyncSession, obj: News) -> None:
    await db.delete(obj)
    await db.commit()
