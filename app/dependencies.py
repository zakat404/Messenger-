# app/dependencies.py
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import decode_access_token
from .config import settings
from .database import get_session
from . import models
from .utils import http_error_401

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_db(session: AsyncSession = Depends(get_session)):
    return session

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        http_error_401("Invalid authentication credentials")

    user_id: int = payload.get("user_id")
    if user_id is None:
        http_error_401("Invalid authentication credentials")

    user = await db.get(models.User, user_id)
    if not user:
        http_error_401("User not found")

    return user
