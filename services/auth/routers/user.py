from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from crud.user import create_user, update_user, delete_user, get_user_by_email
from core.rabbit import publish_user_event
from deps.db import get_db
from deps.user import get_current_user
from schemas.user import UserCreate, UserUpdate, UserOut
import httpx
from loguru import logger


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    team_id = None
    if user_in.team_code:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"http://team:8000/teams/by-code/{user_in.team_code}"
            )
            if resp.status_code == 200:
                team = resp.json()
                team_id = team["id"]
            else:
                raise HTTPException(status_code=400, detail="Некорректный код команды")
    try:
        user = await create_user(db, user_in, team_id=team_id)
        logger.info(f"User created id={user.id} email={user.email}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # Публикуем событие о создании пользователя
    await publish_user_event(
        "created",
        {
            "id": user.id,
            "email": user.email,
            "hashed_password": user.hashed_password,
            "full_name": user.full_name,
            "status": (
                user.status.value if hasattr(user.status, "value") else str(user.status)
            ),
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
            "team_id": user.team_id,
            "is_active": True,
            "is_admin": False,
        },
    )
    return UserOut.model_validate(user)


@router.put("/me", response_model=UserOut)
async def update_me(
    user_in: UserUpdate,
    current_user: UserOut = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    db_user = await get_user_by_email(db, current_user.email)
    user = await update_user(db, db_user, user_in)
    return UserOut.model_validate(user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    current_user: UserOut = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    db_user = await get_user_by_email(db, current_user.email)
    await delete_user(db, db_user)
    return
