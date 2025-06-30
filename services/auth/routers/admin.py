from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from deps.db import get_db
from deps.user import get_current_user
from schemas.user import UserOut, UserStatus, UserRole
from crud.user import get_user_by_id, admin_update_user_fields
from sqlalchemy import update
from models.user import User
from typing import Optional

router = APIRouter(prefix="/admin", tags=["admin"])


def is_admin(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    if current_user.role not in [UserRole.admin, UserRole.superadmin]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    return current_user


@router.put("/users/{user_id}/status", response_model=UserOut)
async def change_user_status(
    user_id: int,
    status_in: UserStatus,
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(is_admin),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user = await admin_update_user_fields(db, user, status=status_in)
    return UserOut.model_validate(user)


@router.put("/users/{user_id}/role", response_model=UserOut)
async def change_user_role(
    user_id: int,
    role_in: UserRole,
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(is_admin),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user = await admin_update_user_fields(db, user, role=role_in)
    return UserOut.model_validate(user)
