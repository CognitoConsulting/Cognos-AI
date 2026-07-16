from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMBaseModel


class CompanyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    status: str = "active"
    ai_key_mode: str = "platform_managed"
    ai_subscription_enabled: bool = False


class CompanyRead(ORMBaseModel):
    id: UUID
    name: str
    status: str
    ai_key_mode: str
    ai_subscription_enabled: bool
    created_at: datetime
