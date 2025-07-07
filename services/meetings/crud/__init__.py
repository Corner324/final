from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import select, delete, and_, exists, or_, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Meeting, meeting_participants
from schemas import MeetingCreate, MeetingUpdate


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------


async def _has_time_conflict(
    db: AsyncSession,
    participants: List[int],
    start_time: datetime,
    end_time: datetime,
    exclude_meeting_id: int | None = None,
) -> bool:
    """Проверяем, что у любого из *participants* нет пересечения с другими встречами."""

    stmt = (
        select(meeting_participants.c.user_id)
        .join(Meeting, Meeting.id == meeting_participants.c.meeting_id)
        .where(meeting_participants.c.user_id.in_(participants))
        .where(
            or_(
                # новая встреча начинается внутри существующей
                and_(start_time >= Meeting.start_time, start_time < Meeting.end_time),
                # новая встреча заканчивается внутри существующей
                and_(end_time > Meeting.start_time, end_time <= Meeting.end_time),
                # существующая встреча полностью внутри новой
                and_(start_time <= Meeting.start_time, end_time >= Meeting.end_time),
            )
        )
    )

    if exclude_meeting_id is not None:
        stmt = stmt.where(Meeting.id != exclude_meeting_id)

    res = await db.execute(stmt)
    conflict = res.first() is not None
    return conflict


# ---------------------------------------------------------------------------
# CRUD-операции
# ---------------------------------------------------------------------------


async def create_meeting(db: AsyncSession, data: MeetingCreate) -> Meeting:
    # 1) Проверяем внешний календарный сервис: если слот занят глобальным событием
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://calendar:8000/calendar/availability",
                json={
                    "start_time": data.start_time.isoformat(),
                    "end_time": data.end_time.isoformat(),
                },
                timeout=5.0,
            )
            if resp.status_code == 200 and resp.json().get("available") is False:
                raise ValueError("Время занято в календаре")
    except httpx.HTTPError:
        # Если календарь недоступен, продолжаем, полагаясь на локальную проверку
        pass

    # 2) Проверяем пересечения с другими встречами внутри сервиса
    if await _has_time_conflict(
        db, data.participants + [data.organizer_id], data.start_time, data.end_time
    ):
        raise ValueError("Время занято у одного из участников")

    meeting_dict = data.model_dump(exclude={"participants"})
    participants = data.participants or []

    meeting = Meeting(**meeting_dict)
    db.add(meeting)
    await db.flush()  # получаем meeting.id без коммита

    # Вставляем участников (организатора добавляем автоматически)
    all_participants = list(set(participants + [data.organizer_id]))
    await db.execute(
        insert(meeting_participants),
        [{"meeting_id": meeting.id, "user_id": pid} for pid in all_participants],
    )

    await db.commit()

    # Повторно загружаем объект вместе с участниками одним запросом
    meeting = await db.get(
        Meeting, meeting.id, options=(selectinload(Meeting.participants),)
    )
    return meeting


async def get_meeting(db: AsyncSession, meeting_id: int) -> Meeting | None:
    res = await db.execute(
        select(Meeting)
        .options(selectinload(Meeting.participants))
        .where(Meeting.id == meeting_id)
    )
    return res.scalar_one_or_none()


async def get_meetings(db: AsyncSession, team_id: int | None = None) -> list[Meeting]:
    stmt = (
        select(Meeting)
        .options(selectinload(Meeting.participants))
        .order_by(Meeting.start_time.desc())
    )
    if team_id is not None:
        stmt = stmt.where(Meeting.team_id == team_id)
    res = await db.execute(stmt)
    return res.scalars().all()


async def update_meeting(
    db: AsyncSession, meeting: Meeting, data: MeetingUpdate
) -> Meeting:
    payload = data.model_dump(exclude_unset=True, exclude={"participants"})

    if (
        "start_time" in payload
        or "end_time" in payload
        or data.participants is not None
    ):
        new_start = payload.get("start_time", meeting.start_time)
        new_end = payload.get("end_time", meeting.end_time)
        new_participants = (
            data.participants
            if data.participants is not None
            else [p.user_id for p in meeting.participants]
        )

        if await _has_time_conflict(
            db, new_participants, new_start, new_end, exclude_meeting_id=meeting.id
        ):
            raise ValueError("Время занято у одного из участников")
        # Также проверяем календарный сервис
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "http://calendar:8000/calendar/availability",
                    json={
                        "start_time": new_start.isoformat(),
                        "end_time": new_end.isoformat(),
                    },
                    timeout=5.0,
                )
                if resp.status_code == 200 and resp.json().get("available") is False:
                    raise ValueError("Время занято в календаре")
        except httpx.HTTPError:
            pass

    for k, v in payload.items():
        setattr(meeting, k, v)

    # Обновляем участников
    if data.participants is not None:
        await db.execute(
            delete(meeting_participants).where(
                meeting_participants.c.meeting_id == meeting.id
            )
        )
        all_participants = list(set(data.participants + [meeting.organizer_id]))
        await db.execute(
            insert(meeting_participants),
            [{"meeting_id": meeting.id, "user_id": pid} for pid in all_participants],
        )

    await db.commit()
    await db.refresh(meeting)
    return meeting


async def delete_meeting(db: AsyncSession, meeting: Meeting) -> None:
    await db.delete(meeting)
    await db.commit()
