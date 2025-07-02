from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import enum
from datetime import datetime


class UserStatus(str, enum.Enum):
    active = "active"
    invited = "invited"
    blocked = "blocked"
    deleted = "deleted"


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    status: UserStatus = UserStatus.active
    role: UserRole = UserRole.user
    team_id: Optional[int] = None
    is_active: bool = True
    is_admin: bool = False


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None
    team_code: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=8)
    status: Optional[UserStatus] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
