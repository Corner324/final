from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from ..models import Meeting
from ..schemas import MeetingCreate


async def create_meeting(db: AsyncSession, data: MeetingCreate) -> Meeting:
    meeting = Meeting(**data.model_dump())
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    return meeting


async def get_meeting(db: AsyncSession, meeting_id: int) -> Meeting | None:
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    return result.scalar_one_or_none()


async def get_all_meetings(db: AsyncSession) -> list[Meeting]:
    result = await db.execute(select(Meeting).order_by(Meeting.scheduled_at.desc()))
    return result.scalars().all()


async def delete_meeting(db: AsyncSession, meeting_id: int) -> None:
    await db.execute(delete(Meeting).where(Meeting.id == meeting_id))
    await db.commit()
