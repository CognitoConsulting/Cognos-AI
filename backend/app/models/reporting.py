from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProgressEntry(Base):
    __tablename__ = "progress_entries"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    entered_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    source_whatsapp_message_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("whatsapp_messages.id"), nullable=True
    )
    assistant_conversation_state_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("assistant_conversation_states.id"), nullable=True
    )
    activity_id: Mapped[UUID | None] = mapped_column(ForeignKey("activities.id"), nullable=True)
    activity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    area_id: Mapped[UUID | None] = mapped_column(ForeignKey("project_locations.id"), nullable=True)
    sub_area_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("project_locations.id"), nullable=True
    )
    location_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    unit_id: Mapped[UUID | None] = mapped_column(ForeignKey("units.id"), nullable=True)
    unit_symbol: Mapped[str | None] = mapped_column(String(40), nullable=True)
    work_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="confirmed", nullable=False)
    original_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class ManpowerEntry(Base):
    __tablename__ = "manpower_entries"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    entered_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    source_whatsapp_message_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("whatsapp_messages.id"), nullable=True
    )
    assistant_conversation_state_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("assistant_conversation_states.id"), nullable=True
    )
    trade_name: Mapped[str] = mapped_column(String(120), nullable=False)
    worker_count: Mapped[int] = mapped_column(nullable=False)
    area_id: Mapped[UUID | None] = mapped_column(ForeignKey("project_locations.id"), nullable=True)
    sub_area_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("project_locations.id"), nullable=True
    )
    location_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    work_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="confirmed", nullable=False)
    original_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class MaterialTransaction(Base):
    __tablename__ = "material_transactions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    entered_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    source_whatsapp_message_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("whatsapp_messages.id"), nullable=True
    )
    assistant_conversation_state_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("assistant_conversation_states.id"), nullable=True
    )
    transaction_type: Mapped[str] = mapped_column(String(40), nullable=False)
    material_name: Mapped[str] = mapped_column(String(255), nullable=False)
    boq_item_id: Mapped[UUID | None] = mapped_column(ForeignKey("boq_items.id"), nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    unit_id: Mapped[UUID | None] = mapped_column(ForeignKey("units.id"), nullable=True)
    unit_symbol: Mapped[str | None] = mapped_column(String(40), nullable=True)
    supplier_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    issued_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    purpose: Mapped[str | None] = mapped_column(String(255), nullable=True)
    area_id: Mapped[UUID | None] = mapped_column(ForeignKey("project_locations.id"), nullable=True)
    sub_area_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("project_locations.id"), nullable=True
    )
    location_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="confirmed", nullable=False)
    proof_status: Mapped[str] = mapped_column(String(50), default="not_attached", nullable=False)
    original_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class MaterialStockBalance(Base):
    __tablename__ = "material_stock_balances"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "material_name",
            "unit_symbol",
            name="uq_material_stock_project_material_unit",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    material_name: Mapped[str] = mapped_column(String(255), nullable=False)
    boq_item_id: Mapped[UUID | None] = mapped_column(ForeignKey("boq_items.id"), nullable=True)
    unit_id: Mapped[UUID | None] = mapped_column(ForeignKey("units.id"), nullable=True)
    unit_symbol: Mapped[str] = mapped_column(String(40), nullable=False)
    total_received: Mapped[Decimal] = mapped_column(Numeric(14, 3), default=0, nullable=False)
    total_issued: Mapped[Decimal] = mapped_column(Numeric(14, 3), default=0, nullable=False)
    current_balance: Mapped[Decimal] = mapped_column(Numeric(14, 3), default=0, nullable=False)
    low_stock_threshold: Mapped[Decimal | None] = mapped_column(Numeric(14, 3), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class MediaFile(Base):
    __tablename__ = "media_files"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    uploaded_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    source_whatsapp_message_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("whatsapp_messages.id"), nullable=True
    )
    linked_entity_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    linked_entity_id: Mapped[UUID | None] = mapped_column(nullable=True)
    media_type: Mapped[str] = mapped_column(String(50), nullable=False)
    storage_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider_media_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    processing_status: Mapped[str] = mapped_column(String(50), default="stored", nullable=False)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class VoiceNote(Base):
    __tablename__ = "voice_notes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    uploaded_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    source_whatsapp_message_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("whatsapp_messages.id"), nullable=True
    )
    storage_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider_media_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    transcription_status: Mapped[str] = mapped_column(String(50), nullable=False)
    transcription_provider: Mapped[str | None] = mapped_column(String(120), nullable=True)
    transcript_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcript_language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
