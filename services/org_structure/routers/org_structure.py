from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from deps.db import get_db
from crud.org_structure import (
    create_department,
    get_departments,
    create_position,
    get_positions,
    create_org_member,
    get_org_members,
    update_department,
    delete_department,
    update_position,
    delete_position,
    update_org_member,
    delete_org_member,
)
from schemas.org_structure import (
    DepartmentCreate,
    DepartmentOut,
    DepartmentUpdate,
    PositionCreate,
    PositionOut,
    PositionUpdate,
    OrgMemberCreate,
    OrgMemberOut,
    OrgMemberUpdate,
)
from typing import List
from schemas.org_structure import OrgMemberTree
from models.org_structure import OrgMember


def _build_tree(members: list[OrgMember]) -> list[OrgMemberTree]:
    """Преобразуем плоский список ORM-объектов в дерево OrgMemberTree."""
    id_map: dict[int, OrgMemberTree] = {}
    roots: list[OrgMemberTree] = []

    for m in members:
        id_map[m.id] = OrgMemberTree(
            id=m.id,
            user_id=m.user_id,
            position_id=m.position_id,
            manager_id=m.manager_id,
            team_id=m.team_id,
            children=[],
        )

    for node in id_map.values():
        if node.manager_id and node.manager_id in id_map:
            id_map[node.manager_id].children.append(node)
        else:
            roots.append(node)
    return roots


router = APIRouter(prefix="/org-structure", tags=["org_structure"])


@router.post("/departments", response_model=DepartmentOut)
async def add_department(data: DepartmentCreate, db: AsyncSession = Depends(get_db)):
    return await create_department(db, data)


@router.patch("/departments/{dept_id}", response_model=DepartmentOut)
async def edit_department(
    dept_id: int, data: DepartmentUpdate, db: AsyncSession = Depends(get_db)
):
    depts = (
        await get_departments(db, team_id=data.team_id)
        if hasattr(data, "team_id")
        else None
    )
    from models.org_structure import Department

    dept = None
    if depts is None:
        res = await db.get(Department, dept_id)
        dept = res
    else:
        dept = next((d for d in depts if d.id == dept_id), None)
    if not dept:
        raise HTTPException(404, detail="Department not found")
    dept = await update_department(db, dept, data)
    return dept


@router.delete("/departments/{dept_id}", status_code=204)
async def remove_department(dept_id: int, db: AsyncSession = Depends(get_db)):
    from models.org_structure import Department

    dept = await db.get(Department, dept_id)
    if not dept:
        raise HTTPException(404, detail="Department not found")
    await delete_department(db, dept)
    return None


@router.get("/departments", response_model=List[DepartmentOut])
async def list_departments(team_id: int, db: AsyncSession = Depends(get_db)):
    return await get_departments(db, team_id)


@router.post("/positions", response_model=PositionOut)
async def add_position(data: PositionCreate, db: AsyncSession = Depends(get_db)):
    return await create_position(db, data)


@router.patch("/positions/{pos_id}", response_model=PositionOut)
async def edit_position(
    pos_id: int, data: PositionUpdate, db: AsyncSession = Depends(get_db)
):
    from models.org_structure import Position

    pos = await db.get(Position, pos_id)
    if not pos:
        raise HTTPException(404, detail="Position not found")
    pos = await update_position(db, pos, data)
    return pos


@router.delete("/positions/{pos_id}", status_code=204)
async def remove_position(pos_id: int, db: AsyncSession = Depends(get_db)):
    from models.org_structure import Position

    pos = await db.get(Position, pos_id)
    if not pos:
        raise HTTPException(404, detail="Position not found")
    await delete_position(db, pos)
    return None


@router.get("/positions", response_model=List[PositionOut])
async def list_positions(department_id: int, db: AsyncSession = Depends(get_db)):
    return await get_positions(db, department_id)


@router.post("/members", response_model=OrgMemberOut)
async def add_member(data: OrgMemberCreate, db: AsyncSession = Depends(get_db)):
    return await create_org_member(db, data)


@router.patch("/members/{member_id}", response_model=OrgMemberOut)
async def edit_member(
    member_id: int, data: OrgMemberUpdate, db: AsyncSession = Depends(get_db)
):
    from models.org_structure import OrgMember

    mem = await db.get(OrgMember, member_id)
    if not mem:
        raise HTTPException(404, detail="Member not found")
    mem = await update_org_member(db, mem, data)
    return mem


@router.delete("/members/{member_id}", status_code=204)
async def remove_member(member_id: int, db: AsyncSession = Depends(get_db)):
    from models.org_structure import OrgMember

    mem = await db.get(OrgMember, member_id)
    if not mem:
        raise HTTPException(404, detail="Member not found")
    await delete_org_member(db, mem)
    return None


@router.get("/members", response_model=List[OrgMemberOut])
async def list_members(team_id: int, db: AsyncSession = Depends(get_db)):
    return await get_org_members(db, team_id)


@router.get("/members/hierarchy", response_model=list[OrgMemberTree])
async def hierarchy(team_id: int, db: AsyncSession = Depends(get_db)):
    members = await get_org_members(db, team_id)
    return _build_tree(members)
