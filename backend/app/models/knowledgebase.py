from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProjectKnowledgeUpload(Base):
    __tablename__ = "project_knowledge_uploads"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    uploaded_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    upload_type: Mapped[str] = mapped_column(String(80), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class ProjectLocation(Base):
    __tablename__ = "project_locations"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "parent_location_id",
            "name",
            name="uq_project_locations_parent_name",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    parent_location_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("project_locations.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location_type: Mapped[str] = mapped_column(String(80), nullable=False)
    code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    children = relationship("ProjectLocation")


class Unit(Base):
    __tablename__ = "units"
    __table_args__ = (
        UniqueConstraint("company_id", "name", name="uq_units_company_name"),
        UniqueConstraint("company_id", "symbol", name="uq_units_company_symbol"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    symbol: Mapped[str] = mapped_column(String(40), nullable=False)
    unit_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class Activity(Base):
    __tablename__ = "activities"
    __table_args__ = (
        UniqueConstraint("company_id", "name", name="uq_activities_company_name"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True)
    default_unit_id: Mapped[UUID | None] = mapped_column(ForeignKey("units.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class ActivitySynonym(Base):
    __tablename__ = "activity_synonyms"
    __table_args__ = (
        UniqueConstraint("activity_id", "synonym", name="uq_activity_synonyms_activity_synonym"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    activity_id: Mapped[UUID] = mapped_column(ForeignKey("activities.id"), nullable=False)
    synonym: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class BOQItem(Base):
    __tablename__ = "boq_items"
    __table_args__ = (
        UniqueConstraint("project_id", "item_code", name="uq_boq_items_project_item_code"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    item_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    item_description: Mapped[str] = mapped_column(Text, nullable=False)
    planned_quantity: Mapped[float | None] = mapped_column(Numeric(14, 3), nullable=True)
    unit_id: Mapped[UUID | None] = mapped_column(ForeignKey("units.id"), nullable=True)
    material_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    activity_id: Mapped[UUID | None] = mapped_column(ForeignKey("activities.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class ProjectScheduleItem(Base):
    __tablename__ = "project_schedule_items"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    activity_id: Mapped[UUID | None] = mapped_column(ForeignKey("activities.id"), nullable=True)
    activity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    planned_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    planned_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    area_id: Mapped[UUID | None] = mapped_column(ForeignKey("project_locations.id"), nullable=True)
    sub_area_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("project_locations.id"), nullable=True
    )
    planned_quantity: Mapped[float | None] = mapped_column(Numeric(14, 3), nullable=True)
    unit_id: Mapped[UUID | None] = mapped_column(ForeignKey("units.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
