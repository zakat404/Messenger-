import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from ..models import Message, Chat
from ..schemas import MessageCreate

class MessageService:
    @staticmethod
    async def create_message(db: AsyncSession, sender_id: int, msg_in: MessageCreate):
        result = await db.execute(select(Chat).where(Chat.id == msg_in.chat_id))
        chat = result.scalars().first()
        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

        new_message = Message(
            chat_id=msg_in.chat_id,
            sender_id=sender_id,
            text=msg_in.text,
            timestamp=datetime.datetime.utcnow(),
            client_message_id=msg_in.client_message_id,
        )
        db.add(new_message)
        try:
            await db.commit()
            await db.refresh(new_message)
            return new_message
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate message detected."
            )

    @staticmethod
    async def mark_as_read(db: AsyncSession, message_id: int):
        result = await db.execute(select(Message).where(Message.id == message_id))
        message = result.scalars().first()
        if not message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
        message.is_read = True
        db.add(message)
        try:
            await db.commit()
            await db.refresh(message)
            return message
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
