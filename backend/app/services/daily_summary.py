from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    DailySummaryMessage,
    DailySummarySetting,
    ManpowerEntry,
    MaterialStockBalance,
    MaterialTransaction,
    MediaFile,
    ProgressEntry,
    Project,
    ProjectUser,
    User,
)
from app.services.whatsapp_provider import queue_outbound_text_message

DEFAULT_SUMMARY_TIME = time(19, 0)


@dataclass(frozen=True)
class DailySummaryRecipient:
    user_id: UUID
    name: str
    phone: str


def get_or_create_daily_summary_setting(
    db: Session,
    *,
    company_id: UUID,
    project: Project,
) -> DailySummarySetting:
    setting = db.scalar(
        select(DailySummarySetting)
        .where(DailySummarySetting.company_id == company_id)
        .where(DailySummarySetting.project_id == project.id)
    )
    if setting:
        return setting

    setting = DailySummarySetting(
        company_id=company_id,
        project_id=project.id,
        enabled=True,
        send_time_local=DEFAULT_SUMMARY_TIME,
        timezone=project.timezone,
        recipient_scope="dashboard_users",
    )
    db.add(setting)
    db.flush()
    return setting


def build_daily_summary_preview(
    db: Session,
    *,
    company_id: UUID,
    project: Project,
    summary_date: date,
) -> str:
    progress_entries = _progress_entries(db, company_id, project.id, summary_date)
    manpower_entries = _manpower_entries(db, company_id, project.id, summary_date)
    material_transactions = _material_transactions(db, company_id, project.id, summary_date)
    media_count = _media_count(db, company_id, project.id, summary_date)
    low_stock_items = _low_stock_items(db, company_id, project.id)

    progress_lines = [_progress_line(entry) for entry in progress_entries[:5]]
    manpower_total = sum(entry.worker_count for entry in manpower_entries)
    manpower_by_trade = _manpower_by_trade(manpower_entries)
    received_count = sum(
        1 for entry in material_transactions if entry.transaction_type == "received"
    )
    issued_count = sum(1 for entry in material_transactions if entry.transaction_type == "issued")
    missing_proof_count = sum(
        1 for entry in material_transactions if entry.proof_status != "attached"
    )

    lines = [
        f"Cognos AI daily summary for {project.name}",
        f"Date: {summary_date.isoformat()}",
        "",
        "Progress:",
    ]
    lines.extend(progress_lines or ["- No progress entries recorded today."])
    lines.extend(
        [
            "",
            "Manpower:",
            f"- Total workers recorded: {manpower_total}",
        ]
    )
    lines.extend(
        [f"- {trade}: {count}" for trade, count in manpower_by_trade.items()]
        or ["- No manpower entries recorded today."]
    )
    lines.extend(
        [
            "",
            "Materials:",
            f"- Received entries: {received_count}",
            f"- Issued entries: {issued_count}",
            f"- Entries missing proof: {missing_proof_count}",
            "",
            "Images / proof:",
            f"- Files recorded today: {media_count}",
            "",
            "Stock attention:",
        ]
    )
    lines.extend(
        [
            f"- {item.material_name}: {_format_decimal(item.current_balance)} {item.unit_symbol}"
            for item in low_stock_items[:5]
        ]
        or ["- No low-stock items flagged."]
    )
    lines.extend(
        [
            "",
            "This is an automatic project summary. Please open the dashboard for full details and Excel export.",
        ]
    )
    return "\n".join(lines)


def daily_summary_recipients(
    db: Session,
    *,
    company_id: UUID,
    project_id: UUID,
) -> list[DailySummaryRecipient]:
    rows = db.execute(
        select(User)
        .join(ProjectUser, ProjectUser.user_id == User.id)
        .where(User.company_id == company_id)
        .where(User.is_active.is_(True))
        .where(User.phone.is_not(None))
        .where(ProjectUser.project_id == project_id)
        .where(ProjectUser.can_view_dashboard.is_(True))
        .order_by(User.created_at.asc())
    ).scalars()
    return [
        DailySummaryRecipient(user_id=user.id, name=user.name, phone=user.phone)
        for user in rows
        if user.phone
    ]


def send_daily_summary(
    db: Session,
    *,
    company_id: UUID,
    project: Project,
    summary_date: date,
    summary_text: str,
    trigger_type: str,
    triggered_by_user_id: UUID | None,
) -> list[DailySummaryMessage]:
    sent_messages: list[DailySummaryMessage] = []
    for recipient in daily_summary_recipients(
        db,
        company_id=company_id,
        project_id=project.id,
    ):
        outbound = queue_outbound_text_message(
            db=db,
            company_id=company_id,
            user_id=recipient.user_id,
            to_phone=recipient.phone,
            message_text=summary_text,
            reason="daily_summary",
        )
        db.flush()
        summary_message = DailySummaryMessage(
            company_id=company_id,
            project_id=project.id,
            summary_date=summary_date,
            summary_text=summary_text,
            recipient_user_id=recipient.user_id,
            recipient_phone=recipient.phone,
            whatsapp_message_id=outbound.message.id,
            delivery_status=outbound.message.processing_status,
            trigger_type=trigger_type,
            triggered_by_user_id=triggered_by_user_id,
        )
        db.add(summary_message)
        sent_messages.append(summary_message)
    return sent_messages


def _progress_entries(
    db: Session,
    company_id: UUID,
    project_id: UUID,
    summary_date: date,
) -> list[ProgressEntry]:
    return list(
        db.scalars(
            select(ProgressEntry)
            .where(ProgressEntry.company_id == company_id)
            .where(ProgressEntry.project_id == project_id)
            .where(ProgressEntry.work_date == summary_date)
            .order_by(ProgressEntry.created_at.asc())
        ).all()
    )


def _manpower_entries(
    db: Session,
    company_id: UUID,
    project_id: UUID,
    summary_date: date,
) -> list[ManpowerEntry]:
    return list(
        db.scalars(
            select(ManpowerEntry)
            .where(ManpowerEntry.company_id == company_id)
            .where(ManpowerEntry.project_id == project_id)
            .where(ManpowerEntry.work_date == summary_date)
            .order_by(ManpowerEntry.trade_name.asc())
        ).all()
    )


def _material_transactions(
    db: Session,
    company_id: UUID,
    project_id: UUID,
    summary_date: date,
) -> list[MaterialTransaction]:
    return list(
        db.scalars(
            select(MaterialTransaction)
            .where(MaterialTransaction.company_id == company_id)
            .where(MaterialTransaction.project_id == project_id)
            .where(MaterialTransaction.transaction_date == summary_date)
            .order_by(MaterialTransaction.created_at.asc())
        ).all()
    )


def _media_count(
    db: Session,
    company_id: UUID,
    project_id: UUID,
    summary_date: date,
) -> int:
    start = datetime.combine(summary_date, time.min)
    end = datetime.combine(summary_date, time.max)
    return int(
        db.scalar(
            select(func.count(MediaFile.id))
            .where(MediaFile.company_id == company_id)
            .where(MediaFile.project_id == project_id)
            .where(MediaFile.created_at >= start)
            .where(MediaFile.created_at <= end)
        )
        or 0
    )


def _low_stock_items(
    db: Session,
    company_id: UUID,
    project_id: UUID,
) -> list[MaterialStockBalance]:
    return list(
        db.scalars(
            select(MaterialStockBalance)
            .where(MaterialStockBalance.company_id == company_id)
            .where(MaterialStockBalance.project_id == project_id)
            .where(MaterialStockBalance.low_stock_threshold.is_not(None))
            .where(MaterialStockBalance.current_balance <= MaterialStockBalance.low_stock_threshold)
            .order_by(MaterialStockBalance.material_name.asc())
        ).all()
    )


def _manpower_by_trade(entries: list[ManpowerEntry]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for entry in entries:
        totals[entry.trade_name] = totals.get(entry.trade_name, 0) + entry.worker_count
    return totals


def _progress_line(entry: ProgressEntry) -> str:
    quantity = _format_decimal(entry.quantity)
    unit = f" {entry.unit_symbol}" if entry.unit_symbol else ""
    location = entry.location_text or "unspecified location"
    return f"- {entry.activity_name}: {quantity}{unit} at {location}"


def _format_decimal(value: Decimal) -> str:
    formatted = format(value.normalize(), "f")
    if "." not in formatted:
        return formatted
    return formatted.rstrip("0").rstrip(".")
