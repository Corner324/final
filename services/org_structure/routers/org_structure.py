from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from deps.db import get_db
from crud.org_structure import (
    create_department, get_departments,
    create_position, get_positions,
    create_org_member, get_org_members
)
from schemas.org_structure import (
    DepartmentCreate, DepartmentOut,
    PositionCreate, PositionOut,
    OrgMemberCreate, OrgMemberOut
)
from typing import List

router = APIRouter(prefix="/org-structure", tags=["org_structure"])

@router.post("/departments", response_model=DepartmentOut)
async def add_department(data: DepartmentCreate, db: AsyncSession = Depends(get_db)):
    return await create_department(db, data)

@router.get("/departments", response_model=List[DepartmentOut])
async def list_departments(team_id: int, db: AsyncSession = Depends(get_db)):
    return await get_departments(db, team_id)

@router.post("/positions", response_model=PositionOut)
async def add_position(data: PositionCreate, db: AsyncSession = Depends(get_db)):
    return await create_position(db, data)

@router.get("/positions", response_model=List[PositionOut])
async def list_positions(department_id: int, db: AsyncSession = Depends(get_db)):
    return await get_positions(db, department_id)

@router.post("/members", response_model=OrgMemberOut)
async def add_member(data: OrgMemberCreate, db: AsyncSession = Depends(get_db)):
    return await create_org_member(db, data)

@router.get("/members", response_model=List[OrgMemberOut])
async def list_members(team_id: int, db: AsyncSession = Depends(get_db)):
    return await get_org_members(db, team_id)
