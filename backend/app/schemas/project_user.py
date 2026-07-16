from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import ORMBaseModel


class ProjectUserCreate(BaseModel):
    user_id: UUID
    role_on_project: str
    can_enter_progress: bool = False
    can_enter_manpower: bool = False
    can_enter_materials: bool = False
    can_view_dashboard: bool = False


class ProjectUserRead(ORMBaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    role_on_project: str
    can_enter_progress: bool
    can_enter_manpower: bool
    can_enter_materials: bool
    can_view_dashboard: bool
    created_at: datetime
