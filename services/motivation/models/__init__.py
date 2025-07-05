from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Motivation(Base):
    __tablename__ = "motivations"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# ---------------------------------------------------------------------------
# Rating: оценки по задачам
# ---------------------------------------------------------------------------


class Rating(Base):
    """Оценка выполненной задачи по трём критериям."""

    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    task_id = Column(Integer, nullable=False)
    reviewer_id = Column(Integer, nullable=False)
    team_id = Column(Integer, nullable=False, index=True)

    timeliness_score = Column(Integer, nullable=False)
    completeness_score = Column(Integer, nullable=False)
    quality_score = Column(Integer, nullable=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Rating {self.id}: user={self.user_id} task={self.task_id} "
            f"{self.timeliness_score}/{self.completeness_score}/{self.quality_score}>"
        )
