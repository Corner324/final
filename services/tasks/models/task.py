from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"
    cancelled = "cancelled"

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.todo, nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    assignee_id: Mapped[int] = mapped_column(Integer, nullable=False)
    creator_id: Mapped[int] = mapped_column(Integer, nullable=False)
    calendar_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    team_id: Mapped[int] = mapped_column(Integer, nullable=False)
