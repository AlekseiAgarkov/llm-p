import uuid
from datetime import datetime, UTC
from typing import List
from uuid import UUID

from sqlalchemy import String, DateTime, ForeignKey, Index, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC))

    chat_messages: Mapped[List["ChatMessage"]] = relationship("ChatMessage",
                                                              back_populates="user",
                                                              cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_lower_email", func.lower(email), unique=True),
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime,
                                                 nullable=False,
                                                 default=lambda: datetime.now(UTC),
                                                 index=True)

    user: Mapped["User"] = relationship("User",
                                        back_populates="chat_messages")

    __table_args__ = (
        Index("ix_chat_messages_user_created", "user_id", "created_at"),
    )
