from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import (
    AuthContext,
    get_auth_context,
    get_database_session,
    require_company_admin_access,
    require_project_dashboard_access,
)
from app.models import DailySummaryMessage, DailySummarySetting
from app.schemas.daily_summary import (
    DailySummaryMessageRead,
    DailySummaryPreview,
    DailySummarySendRequest,
    DailySummarySendResult,
    DailySummarySettingRead,
    DailySummarySettingUpdate,
)
from app.services.daily_summary import (
    build_daily_summary_preview,
    daily_summary_recipients,
    get_or_create_daily_summary_setting,
    send_daily_summary,
)

router = APIRouter(prefix="/companies/{company_id}/projects/{project_id}/daily-summary")


@router.get("/settings", response_model=DailySummarySettingRead)
def get_daily_summary_settings(
    company_id: UUID,
    project_id: UUID,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_database_session),
) -> DailySummarySetting:
    project = require_project_dashboard_access(db, company_id, project_id, auth)
    setting = get_or_create_daily_summary_setting(
        db,
        company_id=company_id,
        project=project,
    )
    db.commit()
    db.refresh(setting)
    return setting


@router.put("/settings", response_model=DailySummarySettingRead)
def update_daily_summary_settings(
    company_id: UUID,
    project_id: UUID,
    payload: DailySummarySettingUpdate,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_database_session),
) -> DailySummarySetting:
    project = require_project_dashboard_access(db, company_id, project_id, auth)
    require_company_admin_access(db, company_id, auth)
    setting = get_or_create_daily_summary_setting(
        db,
        company_id=company_id,
        project=project,
    )
    setting.enabled = payload.enabled
    setting.send_time_local = payload.send_time_local
    setting.timezone = payload.timezone or project.timezone
    setting.recipient_scope = payload.recipient_scope
    setting.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(setting)
    return setting


@router.get("/preview", response_model=DailySummaryPreview)
def preview_daily_summary(
    company_id: UUID,
    project_id: UUID,
    summary_date: date | None = None,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_database_session),
) -> DailySummaryPreview:
    project = require_project_dashboard_access(db, company_id, project_id, auth)
    setting = get_or_create_daily_summary_setting(
        db,
        company_id=company_id,
        project=project,
    )
    target_date = summary_date or date.today()
    summary_text = build_daily_summary_preview(
        db,
        company_id=company_id,
        project=project,
        summary_date=target_date,
    )
    recipients = daily_summary_recipients(
        db,
        company_id=company_id,
        project_id=project_id,
    )
    db.commit()
    return DailySummaryPreview(
        project_id=project_id,
        summary_date=target_date,
        summary_text=summary_text,
        recipient_count=len(recipients),
        send_time_local=setting.send_time_local,
        timezone=setting.timezone,
    )


@router.post(
    "/send-now",
    response_model=DailySummarySendResult,
    status_code=status.HTTP_201_CREATED,
)
def send_daily_summary_now(
    company_id: UUID,
    project_id: UUID,
    payload: DailySummarySendRequest,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_database_session),
) -> DailySummarySendResult:
    project = require_project_dashboard_access(db, company_id, project_id, auth)
    setting = get_or_create_daily_summary_setting(
        db,
        company_id=company_id,
        project=project,
    )
    target_date = payload.summary_date or date.today()
    recipients = daily_summary_recipients(
        db,
        company_id=company_id,
        project_id=project_id,
    )
    if not setting.enabled:
        db.commit()
        return DailySummarySendResult(
            project_id=project_id,
            summary_date=target_date,
            recipient_count=len(recipients),
            sent_count=0,
            skipped_count=len(recipients),
            messages=[],
        )

    summary_text = build_daily_summary_preview(
        db,
        company_id=company_id,
        project=project,
        summary_date=target_date,
    )
    messages = send_daily_summary(
        db,
        company_id=company_id,
        project=project,
        summary_date=target_date,
        summary_text=summary_text,
        trigger_type=payload.trigger_type,
        triggered_by_user_id=auth.user.id if auth.user else None,
    )
    db.commit()
    for message in messages:
        db.refresh(message)
    return DailySummarySendResult(
        project_id=project_id,
        summary_date=target_date,
        recipient_count=len(recipients),
        sent_count=len(messages),
        skipped_count=max(0, len(recipients) - len(messages)),
        messages=[DailySummaryMessageRead.model_validate(message) for message in messages],
    )


@router.get("/messages", response_model=list[DailySummaryMessageRead])
def list_daily_summary_messages(
    company_id: UUID,
    project_id: UUID,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_database_session),
) -> list[DailySummaryMessage]:
    require_project_dashboard_access(db, company_id, project_id, auth)
    return list(
        db.scalars(
            select(DailySummaryMessage)
            .where(DailySummaryMessage.company_id == company_id)
            .where(DailySummaryMessage.project_id == project_id)
            .order_by(DailySummaryMessage.created_at.desc())
        ).all()
    )
