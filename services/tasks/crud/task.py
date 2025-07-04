from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.task import Task
from schemas.task import TaskCreate, TaskUpdate
import httpx


async def _is_manager_of(creator_id: int, assignee_id: int, team_id: int) -> bool:
    """Проверяем через сервис org_structure, является ли creator менеджером assignee."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"http://org_structure:8000/org-structure/members?team_id={team_id}"
            )
            if resp.status_code != 200:
                return True  # fallback — пропускаем
            members = resp.json()
            assignee_member = next(
                (m for m in members if m["user_id"] == assignee_id), None
            )
            if not assignee_member:
                return True  # нет записи — игнорируем
            # менеджер цепочка
            manager_id = assignee_member.get("manager_id")
            while manager_id:
                if manager_id == creator_id:
                    return True
                mgr = next((m for m in members if m["id"] == manager_id), None)
                if not mgr:
                    break
                manager_id = mgr.get("manager_id")
    except httpx.HTTPError:
        return True
    return creator_id == assignee_id  # self-assign or fallback


async def create_task(db: AsyncSession, data: TaskCreate) -> Task:
    # role check: creator must be manager of assignee
    if not await _is_manager_of(data.creator_id, data.assignee_id, data.team_id):
        raise ValueError("Creator is not manager of assignee")

    # Проверка due_date в календаре исполнителя
    if data.due_date is not None:
        import httpx

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    "http://calendar:8000/calendar/availability",
                    json={
                        "start_time": data.due_date.isoformat(),
                        "end_time": data.due_date.isoformat(),
                        "user_id": data.assignee_id,
                    },
                )
                if resp.status_code == 200 and resp.json().get("available") is False:
                    raise ValueError("Due date conflicts with calendar event")
        except httpx.HTTPError:
            pass

    obj = Task(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_tasks(db: AsyncSession, team_id: int) -> list[Task]:
    res = await db.execute(select(Task).where(Task.team_id == team_id))
    return res.scalars().all()


async def get_task(db: AsyncSession, task_id: int) -> Task | None:
    res = await db.execute(select(Task).where(Task.id == task_id))
    return res.scalar_one_or_none()


async def update_task(db: AsyncSession, task_id: int, data: TaskUpdate) -> Task | None:
    obj = await get_task(db, task_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_task(db: AsyncSession, task_id: int) -> bool:
    obj = await get_task(db, task_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True
