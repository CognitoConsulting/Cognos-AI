from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AssistantParseResult(Base):
    __tablename__ = "assistant_parse_results"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID | None] = mapped_column(ForeignKey("companies.id"), nullable=True)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    whatsapp_message_id: Mapped[UUID] = mapped_column(
        ForeignKey("whatsapp_messages.id"), nullable=False
    )
    intent: Mapped[str] = mapped_column(String(80), nullable=False)
    confidence: Mapped[str] = mapped_column(String(40), nullable=False)
    input_language: Mapped[str | None] = mapped_column(String(40), nullable=True)
    extracted_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    missing_fields: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    validation_status: Mapped[str] = mapped_column(String(50), nullable=False)
    assistant_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_action: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class AssistantConversationState(Base):
    __tablename__ = "assistant_conversation_states"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID | None] = mapped_column(ForeignKey("companies.id"), nullable=True)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    whatsapp_message_id: Mapped[UUID] = mapped_column(
        ForeignKey("whatsapp_messages.id"), nullable=False
    )
    parse_result_id: Mapped[UUID] = mapped_column(
        ForeignKey("assistant_parse_results.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    pending_intent: Mapped[str] = mapped_column(String(80), nullable=False)
    pending_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    missing_fields: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    confirmation_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_user_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
