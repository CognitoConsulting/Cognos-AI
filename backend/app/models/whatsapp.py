from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WhatsAppProviderAccount(Base):
    __tablename__ = "whatsapp_provider_accounts"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "provider_name",
            "phone_number_id",
            name="uq_whatsapp_provider_accounts_company_provider_phone",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(80), nullable=False)
    provider_account_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    webhook_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone_number_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class WhatsAppMessage(Base):
    __tablename__ = "whatsapp_messages"
    __table_args__ = (
        UniqueConstraint(
            "provider_name",
            "provider_message_id",
            name="uq_whatsapp_messages_provider_message_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID | None] = mapped_column(ForeignKey("companies.id"), nullable=True)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    message_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider_name: Mapped[str] = mapped_column(String(80), nullable=False)
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider_account_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_provider_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    processing_status: Mapped[str] = mapped_column(String(50), default="received", nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
