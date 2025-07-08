from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import MotivationCreate, MotivationRead
from crud import (
    create_motivation,
    get_motivation,
    get_all_motivations,
    delete_motivation,
)
from deps.db import get_db
from crud.rating import (
    create_rating,
    get_user_ratings,
    get_team_average,
    get_user_average,
)
from schemas import (
    RatingCreate,
    RatingRead,
    UserMatrixResponse,
    TeamAverageResponse,
)

router = APIRouter(prefix="/motivation", tags=["motivation"])


@router.post("/ratings", response_model=RatingRead, status_code=status.HTTP_201_CREATED)
async def add_rating(data: RatingCreate, db: AsyncSession = Depends(get_db)):
    return await create_rating(db, data)


@router.get("/users/{user_id}/matrix", response_model=UserMatrixResponse)
async def user_matrix(user_id: int, db: AsyncSession = Depends(get_db)):
    ratings = await get_user_ratings(db, user_id)
    avg_quarter = await get_user_average(db, user_id, period_days=90)
    avg_all = await get_user_average(db, user_id, period_days=None)
    return UserMatrixResponse(
        ratings=ratings, average_quarter=avg_quarter, average_all=avg_all
    )


@router.get("/teams/{team_id}/average", response_model=TeamAverageResponse)
async def team_average(team_id: int, db: AsyncSession = Depends(get_db)):
    avg = await get_team_average(db, team_id, period_days=90)
    return TeamAverageResponse(team_id=team_id, average=avg)


@router.get("/", response_model=list[MotivationRead])
async def list_motivations(db: AsyncSession = Depends(get_db)):
    return await get_all_motivations(db)


@router.post("/", response_model=MotivationRead, status_code=status.HTTP_201_CREATED)
async def create(data: MotivationCreate, db: AsyncSession = Depends(get_db)):
    return await create_motivation(db, data)


@router.get("/{motivation_id}", response_model=MotivationRead)
async def get(motivation_id: int, db: AsyncSession = Depends(get_db)):
    motivation = await get_motivation(db, motivation_id)
    if not motivation:
        raise HTTPException(status_code=404, detail="Motivation not found")
    return motivation


@router.delete("/{motivation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(motivation_id: int, db: AsyncSession = Depends(get_db)):
    motivation = await get_motivation(db, motivation_id)
    if not motivation:
        raise HTTPException(status_code=404, detail="Motivation not found")
    await delete_motivation(db, motivation_id)
