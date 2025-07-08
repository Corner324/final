from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from models.user import User, UserStatus, UserRole
from schemas.user import UserCreate, UserUpdate
from core.security import hash_password
from sqlalchemy import update, delete


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession, user_in: UserCreate, team_id: int | None = None
) -> User:
    # Проверяем наличие пользователя заранее
    existing = await get_user_by_email(db, user_in.email)
    if existing:
        raise ValueError("Пользователь с таким email уже существует")

    db_user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        team_id=team_id,
    )
    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)
    except IntegrityError:
        await db.rollback()
        raise ValueError("Пользователь с таким email уже существует")
    return db_user


async def update_user(db: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
    if user_in.full_name:
        db_user.full_name = user_in.full_name
    if user_in.password:
        db_user.hashed_password = hash_password(user_in.password)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, db_user: User) -> None:
    await db.delete(db_user)
    await db.commit()


async def admin_update_user_fields(
    db: AsyncSession,
    user: User,
    status: UserStatus | None = None,
    role: UserRole | None = None,
    team_id: int | None = None,
) -> User:
    if status is not None:
        user.status = status
    if role is not None:
        user.role = role
    if team_id is not None:
        user.team_id = team_id
    await db.commit()
    await db.refresh(user)
    return user
