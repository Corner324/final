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

class PositionBase(BaseModel):
    name: str
    department_id: int

class PositionCreate(PositionBase):
    pass

class PositionOut(PositionBase):
    id: int
    class Config:
        from_attributes = True

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
