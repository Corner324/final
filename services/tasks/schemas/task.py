from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"
    cancelled = "cancelled"


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    due_date: Optional[datetime] = None
    assignee_id: int
    creator_id: int
    calendar_id: Optional[int] = None
    team_id: int


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None
    calendar_id: Optional[int] = None


class TaskOut(TaskBase):
    id: int

    class Config:
        from_attributes = True


# Comments



class TaskCommentCreate(BaseModel):
    text: str
    author_id: int


class TaskCommentOut(BaseModel):
    id: int
    task_id: int
    author_id: int
    text: str
    created_at: datetime

    class Config:
        from_attributes = True
