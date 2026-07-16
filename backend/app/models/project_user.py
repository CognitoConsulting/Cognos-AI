from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProjectUser(Base):
    __tablename__ = "project_users"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_users_project_user"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    role_on_project: Mapped[str] = mapped_column(String(80), nullable=False)
    can_enter_progress: Mapped[bool] = mapped_column(default=False, nullable=False)
    can_enter_manpower: Mapped[bool] = mapped_column(default=False, nullable=False)
    can_enter_materials: Mapped[bool] = mapped_column(default=False, nullable=False)
    can_view_dashboard: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    project = relationship("Project", back_populates="project_users")
    user = relationship("User", back_populates="project_users")

