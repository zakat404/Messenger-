from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from ..models import Chat, User, Message
from ..schemas import ChatCreate


class ChatService:
    @staticmethod
    async def create_chat(db: AsyncSession, chat_in: ChatCreate):
        chat = Chat(name=chat_in.name, chat_type=chat_in.chat_type)
        db.add(chat)
        await db.flush()

        if chat_in.participant_ids:
            stmt = select(User).where(User.id.in_(chat_in.participant_ids))
            result = await db.execute(stmt)
            user_objs = result.scalars().all()
            chat.participants = user_objs

        await db.commit()
        await db.refresh(chat)
        return chat

    @staticmethod
    async def get_chat(db: AsyncSession, chat_id: int):
        stmt = select(Chat).where(Chat.id == chat_id)
        result = await db.execute(stmt)
        chat = result.scalars().first()
        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
        return chat

    @staticmethod
    async def get_history(db: AsyncSession, chat_id: int, limit: int = 20, offset: int = 0):
        stmt = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.timestamp.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        messages = result.scalars().all()
        return messages
