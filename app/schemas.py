from typing import Optional, List
from pydantic import BaseModel, EmailStr
import datetime


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


class ChatCreate(BaseModel):
    name: Optional[str] = None
    chat_type: str = "personal"
    participant_ids: List[int] = []


class ChatOut(BaseModel):
    id: int
    name: str
    chat_type: str

    class Config:
        orm_mode = True


class GroupCreate(BaseModel):
    name: str
    creator_id: int
    participant_ids: List[int] = []


class GroupOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class MessageBase(BaseModel):
    chat_id: int
    text: str
    client_message_id: Optional[str] = None


class MessageCreate(MessageBase):
    pass


class MessageOut(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    text: str
    timestamp: datetime.datetime
    is_read: bool
    client_message_id: Optional[str] = None

    class Config:
        orm_mode = True
