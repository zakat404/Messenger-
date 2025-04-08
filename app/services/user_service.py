from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from .. import models
from ..schemas import UserCreate
from ..auth import get_password_hash, verify_password

class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, user_in: UserCreate):
        result = await db.execute(select(models.User).where(models.User.email == user_in.email))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        hashed_pw = get_password_hash(user_in.password)
        new_user = models.User(
            name=user_in.name,
            email=user_in.email,
            hashed_password=hashed_pw
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    @staticmethod
    async def authenticate(db: AsyncSession, email: str, password: str):
        result = await db.execute(select(models.User).where(models.User.email == email))
        user = result.scalars().first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
