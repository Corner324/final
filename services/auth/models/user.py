from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import relationship, declarative_base
import enum


class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    deleted = "deleted"


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"
    superadmin = "superadmin"


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    status = Column(Enum(UserStatus), default=UserStatus.active, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    team_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # team = relationship("Team", back_populates="users")
