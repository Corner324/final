from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from crud.user import create_user, update_user, delete_user, get_user_by_email
from crud.team import get_team_by_code
from deps.db import get_db
from deps.user import get_current_user
from schemas.user import UserCreate, UserUpdate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    if await get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    team = None
    if user_in.team_code:
        team = await get_team_by_code(db, user_in.team_code)
        if not team:
            raise HTTPException(status_code=400, detail="Invalid team code")
    user = await create_user(db, user_in, team)
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
