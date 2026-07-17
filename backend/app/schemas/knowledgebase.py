from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMBaseModel


class UnitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    symbol: str = Field(min_length=1, max_length=40)
    unit_type: str | None = Field(default=None, max_length=80)


class UnitRead(ORMBaseModel):
    id: UUID
    company_id: UUID
    name: str
    symbol: str
    unit_type: str | None
    created_at: datetime


class ActivityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: str | None = Field(default=None, max_length=120)
    default_unit_id: UUID | None = None


class ActivityRead(ORMBaseModel):
    id: UUID
    company_id: UUID
    name: str
    category: str | None
    default_unit_id: UUID | None
    created_at: datetime


class ActivitySynonymCreate(BaseModel):
    synonym: str = Field(min_length=1, max_length=255)
    language: str | None = Field(default=None, max_length=40)


class ActivitySynonymRead(ORMBaseModel):
    id: UUID
    company_id: UUID
    activity_id: UUID
    synonym: str
    language: str | None
    created_at: datetime


class ProjectLocationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    location_type: str = Field(min_length=1, max_length=80)
    parent_location_id: UUID | None = None
    code: str | None = Field(default=None, max_length=80)


class ProjectLocationRead(ORMBaseModel):
    id: UUID
    company_id: UUID
    project_id: UUID
    parent_location_id: UUID | None
    name: str
    location_type: str
    code: str | None
    created_at: datetime


class BOQItemCreate(BaseModel):
    item_code: str | None = Field(default=None, max_length=120)
    item_description: str = Field(min_length=1)
    planned_quantity: Decimal | None = None
    unit_id: UUID | None = None
    material_name: str | None = Field(default=None, max_length=255)
    activity_id: UUID | None = None


class BOQItemRead(ORMBaseModel):
    id: UUID
    company_id: UUID
    project_id: UUID
    item_code: str | None
    item_description: str
    planned_quantity: Decimal | None
    unit_id: UUID | None
    material_name: str | None
    activity_id: UUID | None
    created_at: datetime


class ProjectScheduleItemCreate(BaseModel):
    activity_id: UUID | None = None
    activity_name: str = Field(min_length=1, max_length=255)
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    area_id: UUID | None = None
    sub_area_id: UUID | None = None
    planned_quantity: Decimal | None = None
    unit_id: UUID | None = None


class ProjectScheduleItemRead(ORMBaseModel):
    id: UUID
    company_id: UUID
    project_id: UUID
    activity_id: UUID | None
    activity_name: str
    planned_start_date: date | None
    planned_end_date: date | None
    area_id: UUID | None
    sub_area_id: UUID | None
    planned_quantity: Decimal | None
    unit_id: UUID | None
    created_at: datetime


class ProjectKnowledgeUploadCreate(BaseModel):
    upload_type: str = Field(min_length=1, max_length=80)
    file_name: str = Field(min_length=1, max_length=255)
    uploaded_by: UUID | None = None
    storage_url: str | None = Field(default=None, max_length=500)
    status: str = "pending"
    error_summary: str | None = None


class ProjectKnowledgeUploadRead(ORMBaseModel):
    id: UUID
    company_id: UUID
    project_id: UUID
    uploaded_by: UUID | None
    upload_type: str
    file_name: str
    storage_url: str | None
    status: str
    error_summary: str | None
    uploaded_at: datetime


class KnowledgeTemplateImportResult(ORMBaseModel):
    upload_id: UUID
    upload_type: str
    status: str
    imported_count: int
    skipped_count: int
    error_count: int
    errors: list[str]
