from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Enum,
    DateTime,
    func,
    Boolean,
)
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()


class UserStatus(str, enum.Enum):
    active = "active"
    invited = "invited"
    blocked = "blocked"
    deleted = "deleted"


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    status = Column(Enum(UserStatus), default=UserStatus.active, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
