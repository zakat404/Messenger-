
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from ..dependencies import get_db, get_current_user
from ..schemas import UserCreate, Token, UserOut
from ..services.user_service import UserService
from ..auth import create_access_token
from ..config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/me", response_model=UserOut)
async def get_me(current_user=Depends(get_current_user)):

    return current_user


@router.post("/register", response_model=Token)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):

    user = await UserService.create_user(db, user_in)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"user_id": user.id}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):

    email = form_data.username
    password = form_data.password

    user = await UserService.authenticate(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"user_id": user.id}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
