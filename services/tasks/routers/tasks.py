from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from deps.db import get_db
from crud.task import create_task, get_tasks, get_task, update_task, delete_task
from schemas.task import TaskCreate, TaskUpdate, TaskOut
from typing import List

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskOut)
async def add_task(data: TaskCreate, db: AsyncSession = Depends(get_db)):
    return await create_task(db, data)

@router.get("/", response_model=List[TaskOut])
async def list_tasks(team_id: int, db: AsyncSession = Depends(get_db)):
    return await get_tasks(db, team_id)

@router.get("/{task_id}", response_model=TaskOut)
async def get_task_by_id(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskOut)
async def update_task_by_id(task_id: int, data: TaskUpdate, db: AsyncSession = Depends(get_db)):
    task = await update_task(db, task_id, data)
    if not task:
        raise HTTPException(404, detail="Task not found")
    return task

@router.delete("/{task_id}")
async def delete_task_by_id(task_id: int, db: AsyncSession = Depends(get_db)):
    ok = await delete_task(db, task_id)
    if not ok:
        raise HTTPException(404, detail="Task not found")
    return {"ok": True}
