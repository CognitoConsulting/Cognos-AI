from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMBaseModel


class ProgressEntryCreate(BaseModel):
    entered_by: UUID | None = None
    source_whatsapp_message_id: UUID | None = None
    assistant_conversation_state_id: UUID | None = None
    activity_id: UUID | None = None
    activity_name: str = Field(min_length=1, max_length=255)
    area_id: UUID | None = None
    sub_area_id: UUID | None = None
    location_text: str | None = Field(default=None, max_length=255)
    quantity: Decimal
    unit_id: UUID | None = None
    unit_symbol: str | None = Field(default=None, max_length=40)
    work_date: date
    status: str = "confirmed"
    original_text: str | None = None
    notes: str | None = None


class ProgressEntryRead(ORMBaseModel):
    id: UUID
    company_id: UUID
    project_id: UUID
    entered_by: UUID | None
    source_whatsapp_message_id: UUID | None
    assistant_conversation_state_id: UUID | None
    activity_id: UUID | None
    activity_name: str
    area_id: UUID | None
    sub_area_id: UUID | None
    location_text: str | None
    quantity: Decimal
    unit_id: UUID | None
    unit_symbol: str | None
    work_date: date
    status: str
    original_text: str | None
    notes: str | None
    created_at: datetime


class ManpowerEntryCreate(BaseModel):
    entered_by: UUID | None = None
    source_whatsapp_message_id: UUID | None = None
    assistant_conversation_state_id: UUID | None = None
    trade_name: str = Field(min_length=1, max_length=120)
    worker_count: int = Field(ge=0)
    area_id: UUID | None = None
    sub_area_id: UUID | None = None
    location_text: str | None = Field(default=None, max_length=255)
    work_date: date
    status: str = "confirmed"
    original_text: str | None = None
    notes: str | None = None


class ManpowerEntryRead(ORMBaseModel):
    id: UUID
    company_id: UUID
    project_id: UUID
    entered_by: UUID | None
    source_whatsapp_message_id: UUID | None
    assistant_conversation_state_id: UUID | None
    trade_name: str
    worker_count: int
    area_id: UUID | None
    sub_area_id: UUID | None
    location_text: str | None
    work_date: date
    status: str
    original_text: str | None
    notes: str | None
    created_at: datetime


class MaterialTransactionCreate(BaseModel):
    entered_by: UUID | None = None
    source_whatsapp_message_id: UUID | None = None
    assistant_conversation_state_id: UUID | None = None
    transaction_type: str = Field(pattern="^(received|issued)$")
    material_name: str = Field(min_length=1, max_length=255)
    boq_item_id: UUID | None = None
    quantity: Decimal
    unit_id: UUID | None = None
    unit_symbol: str | None = Field(default=None, max_length=40)
    supplier_name: str | None = Field(default=None, max_length=255)
    issued_to: str | None = Field(default=None, max_length=255)
    purpose: str | None = Field(default=None, max_length=255)
    area_id: UUID | None = None
    sub_area_id: UUID | None = None
    location_text: str | None = Field(default=None, max_length=255)
    transaction_date: date
    status: str = "confirmed"
    proof_status: str = "not_attached"
    original_text: str | None = None
    notes: str | None = None


class MaterialTransactionRead(ORMBaseModel):
    id: UUID
    company_id: UUID
    project_id: UUID
    entered_by: UUID | None
    source_whatsapp_message_id: UUID | None
    assistant_conversation_state_id: UUID | None
    transaction_type: str
    material_name: str
    boq_item_id: UUID | None
    quantity: Decimal
    unit_id: UUID | None
    unit_symbol: str | None
    supplier_name: str | None
    issued_to: str | None
    purpose: str | None
    area_id: UUID | None
    sub_area_id: UUID | None
    location_text: str | None
    transaction_date: date
    status: str
    proof_status: str
    original_text: str | None
    notes: str | None
    created_at: datetime


class MaterialStockBalanceCreate(BaseModel):
    material_name: str = Field(min_length=1, max_length=255)
    boq_item_id: UUID | None = None
    unit_id: UUID | None = None
    unit_symbol: str = Field(min_length=1, max_length=40)
    total_received: Decimal = Decimal("0")
    total_issued: Decimal = Decimal("0")
    current_balance: Decimal = Decimal("0")
    low_stock_threshold: Decimal | None = None


class MaterialStockBalanceRead(ORMBaseModel):
    id: UUID
    company_id: UUID
    project_id: UUID
    material_name: str
    boq_item_id: UUID | None
    unit_id: UUID | None
    unit_symbol: str
    total_received: Decimal
    total_issued: Decimal
    current_balance: Decimal
    low_stock_threshold: Decimal | None
    updated_at: datetime


class MediaFileCreate(BaseModel):
    uploaded_by: UUID | None = None
    source_whatsapp_message_id: UUID | None = None
    linked_entity_type: str | None = Field(default=None, max_length=80)
    linked_entity_id: UUID | None = None
    media_type: str = Field(min_length=1, max_length=50)
    storage_url: str = Field(min_length=1, max_length=500)
    file_name: str | None = Field(default=None, max_length=255)
    caption: str | None = None
    provider_media_id: str | None = Field(default=None, max_length=255)
    processing_status: str = "stored"
    captured_at: datetime | None = None


class MediaFileRead(ORMBaseModel):
    id: UUID
    company_id: UUID
    project_id: UUID
    uploaded_by: UUID | None
    source_whatsapp_message_id: UUID | None
    linked_entity_type: str | None
    linked_entity_id: UUID | None
    media_type: str
    storage_url: str
    file_name: str | None
    caption: str | None
    provider_media_id: str | None
    processing_status: str
    captured_at: datetime | None
    created_at: datetime


class VoiceNoteRead(ORMBaseModel):
    id: UUID
    company_id: UUID
    project_id: UUID | None
    uploaded_by: UUID | None
    source_whatsapp_message_id: UUID | None
    storage_url: str
    file_name: str | None
    provider_media_id: str | None
    mime_type: str | None
    transcription_status: str
    transcription_provider: str | None
    transcript_text: str | None
    transcript_language: str | None
    error_message: str | None
    captured_at: datetime | None
    created_at: datetime
