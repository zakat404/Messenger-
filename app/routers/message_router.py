from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db, get_current_user
from ..schemas import MessageCreate, MessageOut
from ..services.message_service import MessageService
from ..services.chat_service import ChatService

from ..routers.websocket_router import broadcast_message

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("", response_model=MessageOut)
async def create_message(
    msg_in: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    new_message = await MessageService.create_message(db, current_user.id, msg_in)
    return new_message


@router.post("/{message_id}/read", response_model=MessageOut)
async def mark_message_as_read(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    message = await MessageService.mark_as_read(db, message_id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    chat = await ChatService.get_chat(db, message.chat_id)
    participant_ids = [user.id for user in chat.participants]

    read_receipt_data = {
        "type": "read_receipt",
        "message_id": message.id,
        "chat_id": message.chat_id,
        "reader_id": current_user.id,
        "is_read": message.is_read,
    }

    await broadcast_message(participant_ids, read_receipt_data)

    return message


@router.get("/history/{chat_id}")
async def get_history(
    chat_id: int,
    limit: Optional[int] = 20,
    offset: Optional[int] = 0,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    messages = await ChatService.get_history(db, chat_id, limit, offset)
    return [MessageOut.from_orm(m) for m in messages]
