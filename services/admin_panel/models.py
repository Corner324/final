from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    ForeignKey,
    Enum,
    Boolean,
)
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


class UserStatus(str, enum.Enum):
    """Статусы пользователей."""

    active = "active"
    inactive = "inactive"
    deleted = "deleted"


class UserRole(str, enum.Enum):
    """Роли пользователей."""

    user = "user"
    admin = "admin"
    superadmin = "superadmin"


class Team(Base):
    """Модель команды (компании)."""

    __tablename__ = "teams"

    id: int | None = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(128), nullable=False)
    code: str = Column(String(32), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связь один-ко-многим с пользователями (опционально)
    users = relationship("User", back_populates="team", cascade="all, delete-orphan")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Team {self.id}: {self.name}>"


class User(Base):
    """Модель пользователя."""

    __tablename__ = "users"

    id: int | None = Column(Integer, primary_key=True, index=True)
    email: str = Column(String, unique=True, index=True, nullable=False)
    hashed_password: str = Column(String, nullable=False)
    full_name: str | None = Column(String, nullable=True)
    status = Column(Enum(UserStatus), default=UserStatus.active, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    team_id: int | None = Column(Integer, ForeignKey("teams.id"), nullable=True)
    # Отношение к команде (может быть None)
    team = relationship("Team", back_populates="users", lazy="selectin")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.id}: {self.email}>"
