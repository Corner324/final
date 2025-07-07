from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

# Absolute imports within service package root

from deps.db import get_db  # type: ignore
from crud import (
    create_meeting,
    get_meeting,
    get_meetings,
    update_meeting,
    delete_meeting,
)  # type: ignore
from schemas import MeetingCreate, MeetingUpdate, MeetingOut  # type: ignore


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _to_out(meeting) -> MeetingOut:
    """Convert ORM Meeting to MeetingOut with participants ids list."""
    return MeetingOut.model_validate(
        {
            "id": meeting.id,
            "title": meeting.title,
            "description": meeting.description,
            "start_time": meeting.start_time,
            "end_time": meeting.end_time,
            "team_id": meeting.team_id,
            "organizer_id": meeting.organizer_id,
            "created_at": meeting.created_at,
            "participants": [p.user_id for p in meeting.participants],
        }
    )


router = APIRouter(prefix="/meetings", tags=["meetings"])


# ---------------------------------------------------------------------------
# CRUD энд-пойнты
# ---------------------------------------------------------------------------


@router.post("/", response_model=MeetingOut, status_code=status.HTTP_201_CREATED)
async def create(data: MeetingCreate, db: AsyncSession = Depends(get_db)):
    try:
        meeting = await create_meeting(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # гарантируем, что participants загружены, чтобы избежать MissingGreenlet
    await db.refresh(meeting, attribute_names=["participants"])
    return _to_out(meeting)


@router.get("/", response_model=List[MeetingOut])
async def list_meetings(team_id: int | None = None, db: AsyncSession = Depends(get_db)):
    meetings = await get_meetings(db, team_id)
    return [_to_out(m) for m in meetings]


@router.get("/{meeting_id}", response_model=MeetingOut)
async def get_by_id(meeting_id: int, db: AsyncSession = Depends(get_db)):
    meeting = await get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return _to_out(meeting)


@router.patch("/{meeting_id}", response_model=MeetingOut)
async def update_by_id(
    meeting_id: int,
    data: MeetingUpdate,
    db: AsyncSession = Depends(get_db),
):
    meeting = await get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    try:
        meeting = await update_meeting(db, meeting, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _to_out(meeting)


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_by_id(meeting_id: int, db: AsyncSession = Depends(get_db)):
    meeting = await get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    await delete_meeting(db, meeting)
    return None
