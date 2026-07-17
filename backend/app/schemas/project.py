from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMBaseModel


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    code: str | None = Field(default=None, max_length=80)
    location: str | None = Field(default=None, max_length=255)
    status: str = "active"
    start_date: date | None = None
    end_date: date | None = None
    timezone: str = "Asia/Kolkata"


class ProjectRead(ORMBaseModel):
    id: UUID
    company_id: UUID
    name: str
    code: str | None
    location: str | None
    status: str
    start_date: date | None
    end_date: date | None
    timezone: str
    created_at: datetime
