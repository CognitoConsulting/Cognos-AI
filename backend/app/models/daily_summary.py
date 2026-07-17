from datetime import date, datetime, time
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DailySummarySetting(Base):
    __tablename__ = "daily_summary_settings"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            name="uq_daily_summary_settings_project",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    send_time_local: Mapped[time] = mapped_column(Time(), nullable=False)
    timezone: Mapped[str] = mapped_column(String(80), default="Asia/Kolkata", nullable=False)
    recipient_scope: Mapped[str] = mapped_column(
        String(80), default="dashboard_users", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class DailySummaryMessage(Base):
    __tablename__ = "daily_summary_messages"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    summary_date: Mapped[date] = mapped_column(Date, nullable=False)
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    recipient_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    recipient_phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    whatsapp_message_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("whatsapp_messages.id"), nullable=True
    )
    delivery_status: Mapped[str] = mapped_column(String(50), default="queued", nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(80), default="manual", nullable=False)
    triggered_by_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
