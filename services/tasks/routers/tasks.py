from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from deps.db import get_db
from crud.task import create_task, get_tasks, get_task, update_task, delete_task
from crud.comment import add_comment, get_comments
from schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskOut,
    TaskStatus,
    TaskCommentCreate,
    TaskCommentOut,
)
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskOut)
async def add_task(data: TaskCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await create_task(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[TaskOut])
async def list_tasks(team_id: int, db: AsyncSession = Depends(get_db)):
    return await get_tasks(db, team_id)


@router.get("/{task_id}", response_model=TaskOut)
async def get_task_by_id(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(404, detail="Task not found")
    return task


# ---------------------------------------------------------------------------
# Change status (simplified endpoint)
# ---------------------------------------------------------------------------


class StatusIn(BaseModel):
    status: TaskStatus


@router.patch("/{task_id}/status", response_model=TaskOut)
async def change_status(
    task_id: int, data: StatusIn, db: AsyncSession = Depends(get_db)
):
    task = await update_task(db, task_id, TaskUpdate(status=data.status))
    if not task:
        raise HTTPException(404, detail="Task not found")
    return task


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------


@router.post(
    "/{task_id}/comments",
    response_model=TaskCommentOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    task_id: int, data: TaskCommentCreate, db: AsyncSession = Depends(get_db)
):
    # ensure task exists
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(404, detail="Task not found")
    comment = await add_comment(db, task_id, data)
    return comment


@router.get("/{task_id}/comments", response_model=list[TaskCommentOut])
async def list_comments(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(404, detail="Task not found")
    return await get_comments(db, task_id)


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task_by_id(
    task_id: int, data: TaskUpdate, db: AsyncSession = Depends(get_db)
):
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
