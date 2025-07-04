from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, func
from .task import Base


class TaskComment(Base):
    __tablename__ = "task_comments"
    id = Column(Integer, primary_key=True)
    task_id = Column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    author_id = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
