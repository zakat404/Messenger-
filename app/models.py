import datetime

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
    UniqueConstraint,
    Table
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

users_in_groups = Table(
    "users_in_groups",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("group_id", ForeignKey("groups.id"), primary_key=True),
)

users_in_chats = Table(
    "users_in_chats",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("chat_id", ForeignKey("chats.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    messages = relationship("Message", back_populates="sender", lazy="select")


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"))

    creator = relationship("User", backref="created_groups")
    participants = relationship("User", secondary=users_in_groups, backref="groups", lazy="selectin")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    chat_type = Column(String(20), default="personal")

    messages = relationship("Message", back_populates="chat", lazy="select")
    participants = relationship("User", secondary=users_in_chats, backref="chats", lazy="joined")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    is_read = Column(Boolean, default=False)
    client_message_id = Column(String(50), nullable=True)

    __table_args__ = (
        UniqueConstraint("chat_id", "client_message_id", name="uq_chat_client_msg_id"),
    )

    sender = relationship("User", back_populates="messages", lazy="select")
    chat = relationship("Chat", back_populates="messages", lazy="select")
