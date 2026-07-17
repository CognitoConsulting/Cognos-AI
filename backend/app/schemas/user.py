from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMBaseModel


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    phone: str = Field(min_length=5, max_length=40)
    email: EmailStr | None = None
    role: str
    is_active: bool = True


class UserRead(ORMBaseModel):
    id: UUID
    company_id: UUID
    name: str
    phone: str
    email: str | None
    role: str
    is_active: bool
    created_at: datetime
