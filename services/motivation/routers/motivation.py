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

router = APIRouter(prefix="/motivation", tags=["motivation"])


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
