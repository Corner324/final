from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import CalendarEventCreate, CalendarEventRead
from crud import create_event, get_event, get_all_events, delete_event
from deps.db import get_db
from sqlalchemy import select, or_, and_
from datetime import datetime
from pydantic import BaseModel
from models import CalendarEvent

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/", response_model=list[CalendarEventRead])
async def list_events(user_id: int | None = None, db: AsyncSession = Depends(get_db)):
    return await get_all_events(db, user_id)


@router.post("/", response_model=CalendarEventRead, status_code=status.HTTP_201_CREATED)
async def create(data: CalendarEventCreate, db: AsyncSession = Depends(get_db)):
    return await create_event(db, data)



@router.get("/slots", response_model=list[CalendarEventRead])
async def day_slots(user_id: int, date: datetime, db: AsyncSession = Depends(get_db)):
    start = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=date.tzinfo)
    end = start.replace(hour=23, minute=59, second=59)
    stmt = (
        select(CalendarEvent)
        .where(
            ((CalendarEvent.owner_id == user_id) | (CalendarEvent.is_team_event == 1))
        )
        .where(CalendarEvent.start_time.between(start, end))
    )
    res = await db.execute(stmt)
    return res.scalars().all()



@router.get("/month", response_model=list[CalendarEventRead])
async def month_events(
    user_id: int, year: int, month: int, db: AsyncSession = Depends(get_db)
):
    from calendar import monthrange

    import zoneinfo, datetime as dt

    tz = zoneinfo.ZoneInfo("UTC")
    start = dt.datetime(year, month, 1, 0, 0, 0, tzinfo=tz)
    last_day = monthrange(year, month)[1]
    end = dt.datetime(year, month, last_day, 23, 59, 59, tzinfo=tz)
    stmt = (
        select(CalendarEvent)
        .where(
            ((CalendarEvent.owner_id == user_id) | (CalendarEvent.is_team_event == 1))
        )
        .where(CalendarEvent.start_time.between(start, end))
    )
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/{event_id}", response_model=CalendarEventRead)
async def get(event_id: int, db: AsyncSession = Depends(get_db)):
    event = await get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(event_id: int, db: AsyncSession = Depends(get_db)):
    event = await get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    await delete_event(db, event_id)



class AvailabilityIn(BaseModel):
    start_time: datetime
    end_time: datetime
    user_id: int | None = None


@router.post("/availability")
async def check_availability(data: AvailabilityIn, db: AsyncSession = Depends(get_db)):
    stmt = select(1).where(
        or_(
            # Новый интервал начинается внутри существующего события
            and_(
                data.start_time >= CalendarEvent.start_time,
                data.start_time < CalendarEvent.end_time,
            ),
            # Новый интервал заканчивается внутри существующего события
            and_(
                data.end_time > CalendarEvent.start_time,
                data.end_time <= CalendarEvent.end_time,
            ),
            # Существующее событие внутри нового
            and_(
                data.start_time <= CalendarEvent.start_time,
                data.end_time >= CalendarEvent.end_time,
            ),
        )
    )
    if data.user_id is not None:
        stmt = stmt.where(
            (CalendarEvent.owner_id == data.user_id)
            | (CalendarEvent.is_team_event == 1)
        )
    res = await db.execute(stmt)
    busy = res.first() is not None
    return {"available": not busy}
