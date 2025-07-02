from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from models.user import User, UserStatus, UserRole
from models.team import Team
from schemas.user import UserCreate, UserUpdate
from typing import List, Optional
from sqlalchemy import update as sqlalchemy_update
import hashlib


def hash_password(password: str) -> str:
    # В реальном проекте использовать bcrypt/argon2
    return hashlib.sha256(password.encode()).hexdigest()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    team_id = None
    if user_in.team_code:
        result = await db.execute(select(Team).where(Team.code == user_in.team_code))
        team = result.scalar_one_or_none()
        if not team:
            raise ValueError("Команда с таким кодом не найдена")
        team_id = team.id
    db_user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        team_id=team_id,
        status=UserStatus.active,
        role=UserRole.user,
        is_active=True,
        is_admin=False,
    )
    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)
    except IntegrityError:
        await db.rollback()
        raise ValueError("Пользователь с таким email уже существует")
    return db_user


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def update_user(db: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
    if user_in.full_name is not None:
        db_user.full_name = user_in.full_name
    if user_in.password:
        db_user.hashed_password = hash_password(user_in.password)
    if user_in.status:
        db_user.status = user_in.status
    if user_in.role:
        db_user.role = user_in.role
    if user_in.is_active is not None:
        db_user.is_active = user_in.is_active
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, db_user: User) -> None:
    await db.delete(db_user)
    await db.commit()
