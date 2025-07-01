from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import CalendarEventCreate, CalendarEventRead
from crud import create_event, get_event, get_all_events, delete_event
from deps.db import get_db

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/", response_model=list[CalendarEventRead])
async def list_events(db: AsyncSession = Depends(get_db)):
    return await get_all_events(db)


@router.post("/", response_model=CalendarEventRead, status_code=status.HTTP_201_CREATED)
async def create(data: CalendarEventCreate, db: AsyncSession = Depends(get_db)):
    return await create_event(db, data)


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
