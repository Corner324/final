from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models.team import Team
from schemas.team import TeamCreate, TeamUpdate, TeamOut
from crud.team import (
    create_team,
    get_team_by_id,
    get_team_by_code,
    get_teams,
    update_team,
    delete_team,
)
from typing import List


# Заглушка для Depends
async def get_db():
    pass


router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/", response_model=TeamOut, status_code=status.HTTP_201_CREATED)
async def create_team_view(team_in: TeamCreate, db: AsyncSession = Depends(get_db)):
    team = await create_team(db, team_in)
    return TeamOut.model_validate(team)


@router.get("/", response_model=List[TeamOut])
async def list_teams(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    teams = await get_teams(db, skip, limit)
    return [TeamOut.model_validate(t) for t in teams]


@router.get("/{team_id}", response_model=TeamOut)
async def get_team(team_id: int, db: AsyncSession = Depends(get_db)):
    team = await get_team_by_id(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")
    return TeamOut.model_validate(team)


@router.get("/by-code/{code}", response_model=TeamOut)
async def get_team_by_code_view(code: str, db: AsyncSession = Depends(get_db)):
    team = await get_team_by_code(db, code)
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")
    return TeamOut.model_validate(team)


@router.put("/{team_id}", response_model=TeamOut)
async def update_team_view(
    team_id: int, team_in: TeamUpdate, db: AsyncSession = Depends(get_db)
):
    team = await get_team_by_id(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")
    team = await update_team(db, team, team_in)
    return TeamOut.model_validate(team)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team_view(team_id: int, db: AsyncSession = Depends(get_db)):
    team = await get_team_by_id(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")
    await delete_team(db, team)
    return None
