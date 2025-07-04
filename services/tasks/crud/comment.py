from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.comment import TaskComment
from schemas.task import TaskCommentCreate


async def add_comment(
    db: AsyncSession, task_id: int, data: TaskCommentCreate
) -> TaskComment:
    obj = TaskComment(task_id=task_id, **data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_comments(db: AsyncSession, task_id: int) -> list[TaskComment]:
    res = await db.execute(
        select(TaskComment)
        .where(TaskComment.task_id == task_id)
        .order_by(TaskComment.created_at)
    )
    return res.scalars().all()
