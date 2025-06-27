from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from core.security import decode_access_token
from crud.user import get_user_by_id
from deps.db import get_db
from schemas.user import UserOut

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> UserOut:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    user_id: int = payload.get("sub") if payload else None
    if user_id is None:
        raise credentials_exception
    user = await get_user_by_id(db, user_id)
    if user is None or user.status != "active":
        raise credentials_exception
    return UserOut.model_validate(user)
