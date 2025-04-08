from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db, get_current_user
from ..schemas import ChatCreate, ChatOut
from ..services.chat_service import ChatService

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.post("", response_model=ChatOut)
async def create_chat(
    chat_in: ChatCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    new_chat = await ChatService.create_chat(db, chat_in)
    return new_chat


@router.get("/{chat_id}", response_model=ChatOut)
async def get_chat(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    chat = await ChatService.get_chat(db, chat_id)
    return chat
