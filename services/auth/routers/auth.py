from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from deps.db import get_db
from crud.user import get_user_by_email
from core.security import verify_password, create_access_token
from schemas.user import UserOut
from deps.user import get_current_user


class LoginForm(BaseModel):
    email: str
    password: str


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(form_data: LoginForm, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, form_data.email)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if user.status != "active":
        raise HTTPException(status_code=403, detail="User is not active")
    access_token = create_access_token({"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


# Для поддержки Swagger Authorize (OAuth2 Password Flow)
@router.post("/login-form")
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if user.status != "active":
        raise HTTPException(status_code=403, detail="User is not active")
    access_token = create_access_token({"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
async def get_me(current_user: UserOut = Depends(get_current_user)):
    return current_user
