from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.org_structure import Department, Position, OrgMember
from schemas.org_structure import DepartmentCreate, PositionCreate, OrgMemberCreate

async def create_department(db: AsyncSession, data: DepartmentCreate) -> Department:
    obj = Department(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def get_departments(db: AsyncSession, team_id: int) -> list[Department]:
    res = await db.execute(select(Department).where(Department.team_id == team_id))
    return res.scalars().all()

async def create_position(db: AsyncSession, data: PositionCreate) -> Position:
    obj = Position(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def get_positions(db: AsyncSession, department_id: int) -> list[Position]:
    res = await db.execute(select(Position).where(Position.department_id == department_id))
    return res.scalars().all()

async def create_org_member(db: AsyncSession, data: OrgMemberCreate) -> OrgMember:
    obj = OrgMember(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def get_org_members(db: AsyncSession, team_id: int) -> list[OrgMember]:
    res = await db.execute(select(OrgMember).where(OrgMember.team_id == team_id))
    return res.scalars().all()
