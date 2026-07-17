from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DailySummaryMessage, DailySummarySetting, Project
from app.services.daily_summary import (
    build_daily_summary_preview,
    daily_summary_recipients,
    get_or_create_daily_summary_setting,
    send_daily_summary,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DailySummarySchedulerResult:
    checked_settings: int
    due_settings: int
    sent_projects: int
    sent_messages: int
    skipped_projects: int
    created_default_settings: int


def run_due_daily_summaries(
    db: Session,
    *,
    now_utc: datetime | None = None,
) -> DailySummarySchedulerResult:
    """Send daily summaries that are due at each project's local configured time."""
    current_utc = now_utc or datetime.now(timezone.utc)
    created_settings = ensure_default_daily_summary_settings(db)
    settings = _enabled_settings_for_active_projects(db)
    due_settings = 0
    sent_projects = 0
    sent_messages = 0
    skipped_projects = 0

    for setting, project in settings:
        due_status = _due_status(db, setting, project, current_utc)
        if due_status == "not_due":
            continue
        due_settings += 1

        if due_status != "due":
            skipped_projects += 1
            continue

        recipients = daily_summary_recipients(
            db,
            company_id=setting.company_id,
            project_id=setting.project_id,
        )
        if not recipients:
            skipped_projects += 1
            continue

        local_now = _local_now(current_utc, setting.timezone)
        summary_text = build_daily_summary_preview(
            db,
            company_id=setting.company_id,
            project=project,
            summary_date=local_now.date(),
        )
        messages = send_daily_summary(
            db,
            company_id=setting.company_id,
            project=project,
            summary_date=local_now.date(),
            summary_text=summary_text,
            trigger_type="scheduled",
            triggered_by_user_id=None,
        )
        sent_projects += 1
        sent_messages += len(messages)

    db.commit()
    result = DailySummarySchedulerResult(
        checked_settings=len(settings),
        due_settings=due_settings,
        sent_projects=sent_projects,
        sent_messages=sent_messages,
        skipped_projects=skipped_projects,
        created_default_settings=created_settings,
    )
    logger.info("Daily summary scheduler run completed: %s", result)
    return result


def ensure_default_daily_summary_settings(db: Session) -> int:
    active_projects = list(
        db.scalars(select(Project).where(Project.status == "active").order_by(Project.created_at))
    )
    created_count = 0
    for project in active_projects:
        existing_setting_id = db.scalar(
            select(DailySummarySetting.id).where(DailySummarySetting.project_id == project.id)
        )
        if existing_setting_id:
            continue
        get_or_create_daily_summary_setting(
            db,
            company_id=project.company_id,
            project=project,
        )
        created_count += 1
    if created_count:
        db.flush()
    return created_count


def _enabled_settings_for_active_projects(
    db: Session,
) -> list[tuple[DailySummarySetting, Project]]:
    return list(
        db.execute(
            select(DailySummarySetting, Project)
            .join(Project, Project.id == DailySummarySetting.project_id)
            .where(Project.status == "active")
            .where(DailySummarySetting.enabled.is_(True))
            .order_by(Project.created_at.asc())
        ).all()
    )


def _due_status(
    db: Session,
    setting: DailySummarySetting,
    project: Project,
    now_utc: datetime,
) -> str:
    local_now = _local_now(now_utc, setting.timezone or project.timezone)
    if local_now.time().replace(second=0, microsecond=0) < _minute_precision(
        setting.send_time_local
    ):
        return "not_due"

    already_sent = db.scalar(
        select(DailySummaryMessage.id)
        .where(DailySummaryMessage.company_id == setting.company_id)
        .where(DailySummaryMessage.project_id == setting.project_id)
        .where(DailySummaryMessage.summary_date == local_now.date())
        .limit(1)
    )
    return "already_sent" if already_sent else "due"


def _local_now(now_utc: datetime, timezone_name: str) -> datetime:
    try:
        local_timezone = ZoneInfo(timezone_name)
    except Exception:
        local_timezone = ZoneInfo("Asia/Kolkata")

    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)
    return now_utc.astimezone(local_timezone)


def _minute_precision(value: time) -> time:
    return value.replace(second=0, microsecond=0)
