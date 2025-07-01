from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.task import Task
from schemas.task import TaskCreate, TaskUpdate

async def create_task(db: AsyncSession, data: TaskCreate) -> Task:
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
