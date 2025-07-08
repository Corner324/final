from __future__ import annotations

from pydantic import BaseModel
from typing import Optional


class DepartmentBase(BaseModel):
    name: str
    team_id: int


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentOut(DepartmentBase):
    id: int

    class Config:
        from_attributes = True


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None


class PositionBase(BaseModel):
    name: str
    department_id: int


class PositionCreate(PositionBase):
    pass


class PositionOut(PositionBase):
    id: int

    class Config:
        from_attributes = True


class PositionUpdate(BaseModel):
    name: Optional[str] = None


class OrgMemberBase(BaseModel):
    user_id: int
    position_id: int
    manager_id: Optional[int] = None
    team_id: int


class OrgMemberCreate(OrgMemberBase):
    pass


class OrgMemberOut(OrgMemberBase):
    id: int

    class Config:
        from_attributes = True


class OrgMemberTree(OrgMemberOut):
    children: list["OrgMemberTree"] = []


class OrgMemberUpdate(BaseModel):
    position_id: Optional[int] = None
    manager_id: Optional[int | None] = None
