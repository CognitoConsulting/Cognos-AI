from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMBaseModel


class WhatsAppProviderAccountCreate(BaseModel):
    provider_name: str = Field(min_length=1, max_length=80)
    provider_account_id: str | None = Field(default=None, max_length=255)
    webhook_url: str | None = Field(default=None, max_length=500)
    phone_number_id: str | None = Field(default=None, max_length=255)
    status: str = "active"


class WhatsAppProviderAccountRead(ORMBaseModel):
    id: UUID
    company_id: UUID
    provider_name: str
    provider_account_id: str | None
    webhook_url: str | None
    phone_number_id: str | None
    status: str
    created_at: datetime


class WhatsAppMessageRead(ORMBaseModel):
    id: UUID
    company_id: UUID | None
    user_id: UUID | None
    phone: str | None
    direction: str
    message_text: str | None
    provider_name: str
    provider_message_id: str | None
    provider_account_id: str | None
    processing_status: str
    received_at: datetime


class WhatsAppOutboundTextCreate(BaseModel):
    to_phone: str = Field(min_length=6, max_length=40)
    message_text: str = Field(min_length=1, max_length=2000)
    user_id: UUID | None = None
    provider_name: str | None = Field(default=None, max_length=80)
    provider_account_id: str | None = Field(default=None, max_length=255)
    reason: str = Field(default="manual_test", max_length=80)


class WhatsAppWebhookAccepted(BaseModel):
    status: str
    message_id: UUID | None = None
    processing_status: str
    detail: str
