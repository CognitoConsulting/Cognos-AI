from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMBaseModel


class DailySummarySettingUpdate(BaseModel):
    enabled: bool = True
    send_time_local: time = time(19, 0)
    timezone: str | None = Field(default=None, max_length=80)
    recipient_scope: str = Field(default="dashboard_users", max_length=80)


class DailySummarySettingRead(ORMBaseModel):
    id: UUID
    company_id: UUID
    project_id: UUID
    enabled: bool
    send_time_local: time
    timezone: str
    recipient_scope: str
    created_at: datetime
    updated_at: datetime


class DailySummaryPreview(ORMBaseModel):
    project_id: UUID
    summary_date: date
    summary_text: str
    recipient_count: int
    send_time_local: time
    timezone: str


class DailySummarySendRequest(BaseModel):
    summary_date: date | None = None
    trigger_type: str = Field(default="manual", max_length=80)


class DailySummaryMessageRead(ORMBaseModel):
    id: UUID
    company_id: UUID
    project_id: UUID
    summary_date: date
    summary_text: str
    recipient_user_id: UUID | None
    recipient_phone: str | None
    whatsapp_message_id: UUID | None
    delivery_status: str
    trigger_type: str
    triggered_by_user_id: UUID | None
    created_at: datetime


class DailySummarySendResult(BaseModel):
    project_id: UUID
    summary_date: date
    recipient_count: int
    sent_count: int
    skipped_count: int
    messages: list[DailySummaryMessageRead]
