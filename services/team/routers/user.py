from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserCreate, UserUpdate, UserOut
from crud.user import (
    create_user,
    get_user_by_id,
    get_user_by_email,
    get_users,
    update_user,
    delete_user,
)
from typing import List
from deps.db import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        user = await create_user(db, user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return UserOut.model_validate(user)


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return UserOut.model_validate(user)


@router.get("/", response_model=List[UserOut])
async def list_users(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    users = await get_users(db, skip, limit)
    return [UserOut.model_validate(u) for u in users]


@router.put("/{user_id}", response_model=UserOut)
async def update_user_view(
    user_id: int, user_in: UserUpdate, db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user = await update_user(db, user, user_in)
    return UserOut.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_view(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    await delete_user(db, user)
    return None
