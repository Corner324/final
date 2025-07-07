from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    func,
    Table,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column


Base = declarative_base()


meeting_participants: Table = Table(
    "meeting_participants",
    Base.metadata,
    Column(
        "meeting_id",
        Integer,
        ForeignKey("meetings.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("user_id", Integer, primary_key=True),
)


class MeetingParticipant(Base):
    """association row meeting_id/user_id"""

    __table__ = meeting_participants

    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="participants")


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_time: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)

    organizer_id: Mapped[int] = mapped_column(Integer, nullable=False)
    team_id: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    participants: Mapped[list[MeetingParticipant]] = relationship(
        "MeetingParticipant",
        back_populates="meeting",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
