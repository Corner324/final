from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    owner_id = Column(Integer, nullable=False)
    is_team_event = Column(Integer, default=0, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
