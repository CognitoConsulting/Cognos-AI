from datetime import datetime
from uuid import UUID

from app.schemas.common import ORMBaseModel


class AssistantParseResultRead(ORMBaseModel):
    id: UUID
    company_id: UUID | None
    user_id: UUID | None
    whatsapp_message_id: UUID
    intent: str
    confidence: str
    input_language: str | None
    extracted_data: dict
    missing_fields: list[str]
    validation_status: str
    assistant_summary: str | None
    next_action: str
    created_at: datetime
