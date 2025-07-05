from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import enum


class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    deleted = "deleted"


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"
    superadmin = "superadmin"


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    status: UserStatus = UserStatus.active
    role: UserRole = UserRole.user
    team_id: Optional[int] = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None
    team_code: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=8)


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserInDB(UserBase):
    id: int
    hashed_password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str
