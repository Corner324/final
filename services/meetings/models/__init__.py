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


# ---------------------------------------------------------------------------
# Declarative base for the meetings service
# ---------------------------------------------------------------------------

Base = declarative_base()


# ---------------------------------------------------------------------------
# Association table «meeting_participants» many-to-many: meeting ↔ user
# Мы не пользуемся внешним ключом на таблицу пользователей
# других микросервисов, поэтому FK ссылается только на «meetings».
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Базовая таблица «meetings»
# ---------------------------------------------------------------------------


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

    participants: Mapped[list[int]] = relationship(
        "MeetingParticipant",
        secondary=meeting_participants,
        primaryjoin=id == meeting_participants.c.meeting_id,
        secondaryjoin=meeting_participants.c.user_id,
        viewonly=True,
    )


# Шаблонная модель-обёртка для relationship, чтобы pydantic могла сериализовать list[int]
class MeetingParticipant(Base):
    """Простая обёртка над таблицей связи без переопределения колонок."""

    __table__ = meeting_participants
