from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.org_structure import Department, Position, OrgMember
from schemas.org_structure import (
    DepartmentCreate,
    DepartmentUpdate,
    PositionCreate,
    PositionUpdate,
    OrgMemberCreate,
    OrgMemberUpdate,
)


async def create_department(db: AsyncSession, data: DepartmentCreate) -> Department:
    obj = Department(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_departments(db: AsyncSession, team_id: int) -> list[Department]:
    res = await db.execute(select(Department).where(Department.team_id == team_id))
    return res.scalars().all()


async def update_department(
    db: AsyncSession, obj: Department, data: DepartmentUpdate
) -> Department:
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_department(db: AsyncSession, obj: Department) -> None:
    await db.delete(obj)
    await db.commit()


async def create_position(db: AsyncSession, data: PositionCreate) -> Position:
    obj = Position(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_positions(db: AsyncSession, department_id: int) -> list[Position]:
    res = await db.execute(
        select(Position).where(Position.department_id == department_id)
    )
    return res.scalars().all()


async def update_position(
    db: AsyncSession, obj: Position, data: PositionUpdate
) -> Position:
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_position(db: AsyncSession, obj: Position) -> None:
    await db.delete(obj)
    await db.commit()


async def create_org_member(db: AsyncSession, data: OrgMemberCreate) -> OrgMember:
    obj = OrgMember(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_org_members(db: AsyncSession, team_id: int) -> list[OrgMember]:
    res = await db.execute(select(OrgMember).where(OrgMember.team_id == team_id))
    return res.scalars().all()


async def update_org_member(
    db: AsyncSession, obj: OrgMember, data: OrgMemberUpdate
) -> OrgMember:
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_org_member(db: AsyncSession, obj: OrgMember) -> None:
    await db.delete(obj)
    await db.commit()
