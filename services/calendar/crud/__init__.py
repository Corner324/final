from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models import CalendarEvent
from schemas import CalendarEventCreate


async def create_event(db: AsyncSession, data: CalendarEventCreate) -> CalendarEvent:
    event = CalendarEvent(**data.model_dump())
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def get_event(db: AsyncSession, event_id: int) -> CalendarEvent | None:
    result = await db.execute(select(CalendarEvent).where(CalendarEvent.id == event_id))
    return result.scalar_one_or_none()


async def get_all_events(
    db: AsyncSession, user_id: int | None = None
) -> list[CalendarEvent]:
    stmt = select(CalendarEvent).order_by(CalendarEvent.start_time.desc())
    if user_id is not None:
        stmt = stmt.where(
            (CalendarEvent.owner_id == user_id) | (CalendarEvent.is_team_event == 1)
        )
    result = await db.execute(stmt)
    return result.scalars().all()


async def delete_event(db: AsyncSession, event_id: int) -> None:
    await db.execute(delete(CalendarEvent).where(CalendarEvent.id == event_id))
    await db.commit()
