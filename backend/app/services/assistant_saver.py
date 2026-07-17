from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    AssistantConversationState,
    ManpowerEntry,
    MaterialStockBalance,
    MaterialTransaction,
    ProgressEntry,
    Project,
    ProjectUser,
    User,
)


AFFIRMATIVE_REPLIES = {
    "yes",
    "y",
    "ok",
    "okay",
    "save",
    "confirm",
    "confirmed",
    "haan",
    "ha",
    "han",
    "theek hai",
    "sahi hai",
}


@dataclass(frozen=True)
class ConfirmationSaveResult:
    handled: bool
    processing_status: str
    detail: str
    saved_record_type: str | None = None
    saved_record_count: int = 0


def is_affirmative_confirmation(message_text: str | None) -> bool:
    normalized = (message_text or "").strip().lower().strip(".! ")
    return normalized in AFFIRMATIVE_REPLIES


def save_latest_confirmed_update(
    db: Session,
    user: User,
    confirmation_message_text: str | None,
) -> ConfirmationSaveResult:
    pending_state = _find_latest_pending_confirmation(db, user)
    if not pending_state:
        return ConfirmationSaveResult(
            handled=False,
            processing_status="no_pending_confirmation",
            detail="No pending assistant confirmation was found for this user.",
        )

    project = _resolve_single_project_for_user(db, user)
    pending_state.last_user_message = confirmation_message_text
    pending_state.updated_at = datetime.utcnow()

    if not project:
        pending_state.status = "awaiting_project_selection"
        pending_state.missing_fields = ["project"]
        pending_state.confirmation_prompt = _build_project_selection_prompt(db, user)
        db.commit()
        return ConfirmationSaveResult(
            handled=True,
            processing_status="awaiting_project_selection",
            detail="Confirmation received, but project selection is required before saving.",
        )

    return _save_pending_state_to_project(db, user, pending_state, project)


def save_project_selection_reply(
    db: Session,
    user: User,
    project_selection_text: str | None,
) -> ConfirmationSaveResult:
    pending_state = _find_latest_project_selection_state(db, user)
    if not pending_state:
        return ConfirmationSaveResult(
            handled=False,
            processing_status="no_pending_project_selection",
            detail="No pending project selection was found for this user.",
        )

    pending_state.last_user_message = project_selection_text
    pending_state.updated_at = datetime.utcnow()

    match_result = _match_project_from_text(db, user, project_selection_text)
    if match_result.status == "no_match":
        pending_state.confirmation_prompt = (
            "I could not match that to one of your active projects. "
            "Please send the project name or project code."
        )
        db.commit()
        return ConfirmationSaveResult(
            handled=True,
            processing_status="awaiting_project_selection",
            detail="Project selection was not recognized.",
        )

    if match_result.status == "ambiguous":
        pending_state.confirmation_prompt = (
            "I found more than one matching project. Please send the exact project code."
        )
        db.commit()
        return ConfirmationSaveResult(
            handled=True,
            processing_status="awaiting_project_selection",
            detail="Project selection matched more than one project.",
        )

    return _save_pending_state_to_project(db, user, pending_state, match_result.project)


def _save_pending_state_to_project(
    db: Session,
    user: User,
    pending_state: AssistantConversationState,
    project: Project,
) -> ConfirmationSaveResult:
    if not _user_can_save_intent(db, user, project, pending_state.pending_intent):
        pending_state.status = "permission_denied"
        pending_state.confirmation_prompt = (
            "I understood your confirmation, but your current project role does not allow "
            "you to save this type of update. Please ask your project manager or company admin."
        )
        db.commit()
        return ConfirmationSaveResult(
            handled=True,
            processing_status="permission_denied",
            detail="Confirmation received, but the user is not allowed to save this type of update.",
        )

    record_count = _save_state_to_reporting_records(db, pending_state, project)
    pending_state.status = "saved"
    pending_state.missing_fields = []
    pending_state.confirmation_prompt = "Saved. I have recorded this update."
    pending_state.updated_at = datetime.utcnow()
    db.commit()

    return ConfirmationSaveResult(
        handled=True,
        processing_status=f"saved_{pending_state.pending_intent}",
        detail="Confirmation received and update saved.",
        saved_record_type=pending_state.pending_intent,
        saved_record_count=record_count,
    )


def _find_latest_pending_confirmation(
    db: Session,
    user: User,
) -> AssistantConversationState | None:
    return db.scalar(
        select(AssistantConversationState)
        .where(AssistantConversationState.company_id == user.company_id)
        .where(AssistantConversationState.user_id == user.id)
        .where(AssistantConversationState.status == "awaiting_confirmation")
        .order_by(AssistantConversationState.created_at.desc())
    )


def _find_latest_project_selection_state(
    db: Session,
    user: User,
) -> AssistantConversationState | None:
    return db.scalar(
        select(AssistantConversationState)
        .where(AssistantConversationState.company_id == user.company_id)
        .where(AssistantConversationState.user_id == user.id)
        .where(AssistantConversationState.status == "awaiting_project_selection")
        .order_by(AssistantConversationState.updated_at.desc())
    )


def _resolve_single_project_for_user(db: Session, user: User) -> Project | None:
    available_projects = _projects_available_to_user(db, user)
    if len(available_projects) == 1:
        return available_projects[0]
    return None


def _projects_available_to_user(db: Session, user: User) -> list[Project]:
    if user.role in {"owner", "admin", "company_admin"}:
        return list(
            db.scalars(
                select(Project)
                .where(Project.company_id == user.company_id)
                .where(Project.status == "active")
                .order_by(Project.created_at.desc())
            ).all()
        )

    return list(
        db.scalars(
            select(Project)
            .join(ProjectUser, ProjectUser.project_id == Project.id)
            .where(Project.company_id == user.company_id)
            .where(Project.status == "active")
            .where(ProjectUser.user_id == user.id)
            .order_by(Project.created_at.desc())
        ).all()
    )


@dataclass(frozen=True)
class ProjectMatchResult:
    status: str
    project: Project | None = None


def _match_project_from_text(
    db: Session,
    user: User,
    project_selection_text: str | None,
) -> ProjectMatchResult:
    text = _normalize_project_text(project_selection_text)
    if not text:
        return ProjectMatchResult(status="no_match")

    projects = _projects_available_to_user(db, user)
    exact_matches = [
        project
        for project in projects
        if text in {_normalize_project_text(project.code), _normalize_project_text(project.name)}
    ]
    if len(exact_matches) == 1:
        return ProjectMatchResult(status="matched", project=exact_matches[0])
    if len(exact_matches) > 1:
        return ProjectMatchResult(status="ambiguous")

    partial_matches = [
        project
        for project in projects
        if _project_text_matches(text, project.name) or _project_text_matches(text, project.code)
    ]
    if len(partial_matches) == 1:
        return ProjectMatchResult(status="matched", project=partial_matches[0])
    if len(partial_matches) > 1:
        return ProjectMatchResult(status="ambiguous")

    return ProjectMatchResult(status="no_match")


def _project_text_matches(text: str, candidate: str | None) -> bool:
    candidate_text = _normalize_project_text(candidate)
    return bool(candidate_text and (text in candidate_text or candidate_text in text))


def _normalize_project_text(value: str | None) -> str:
    return " ".join((value or "").strip().lower().replace("-", " ").split())


def _build_project_selection_prompt(db: Session, user: User) -> str:
    projects = _projects_available_to_user(db, user)
    if not projects:
        return (
            "I can save this update, but I could not find an active project for your user. "
            "Please ask your company admin to assign you to a project."
        )

    project_options = []
    for project in projects[:6]:
        label = project.code if project.code else project.name
        project_options.append(f"{project.name} ({label})")

    option_text = "; ".join(project_options)
    return (
        "I can save this update, but I need to know which project it belongs to. "
        f"Please reply with the project name or code. Available projects: {option_text}."
    )


def _user_can_save_intent(
    db: Session,
    user: User,
    project: Project,
    intent: str,
) -> bool:
    if user.role in {"owner", "admin", "company_admin"}:
        return True

    assignment = db.scalar(
        select(ProjectUser)
        .where(ProjectUser.project_id == project.id)
        .where(ProjectUser.user_id == user.id)
    )
    if not assignment:
        return False

    if intent == "progress":
        return assignment.can_enter_progress
    if intent == "manpower":
        return assignment.can_enter_manpower
    if intent in {"material_received", "material_issued"}:
        return assignment.can_enter_materials

    return False


def _save_state_to_reporting_records(
    db: Session,
    state: AssistantConversationState,
    project: Project,
) -> int:
    data = state.pending_data or {}
    work_date = _project_today(project)

    if state.pending_intent == "progress":
        db.add(
            ProgressEntry(
                company_id=project.company_id,
                project_id=project.id,
                entered_by=state.user_id,
                source_whatsapp_message_id=state.whatsapp_message_id,
                assistant_conversation_state_id=state.id,
                activity_name=data.get("activity") or "Unspecified activity",
                location_text=data.get("location"),
                quantity=_decimal(data.get("quantity")),
                unit_symbol=data.get("unit"),
                work_date=work_date,
                status="confirmed",
                original_text=data.get("original_text"),
            )
        )
        return 1

    if state.pending_intent == "manpower":
        trade_counts = data.get("trade_counts") or {}
        for trade_name, worker_count in trade_counts.items():
            db.add(
                ManpowerEntry(
                    company_id=project.company_id,
                    project_id=project.id,
                    entered_by=state.user_id,
                    source_whatsapp_message_id=state.whatsapp_message_id,
                    assistant_conversation_state_id=state.id,
                    trade_name=trade_name,
                    worker_count=int(worker_count),
                    location_text=data.get("location"),
                    work_date=work_date,
                    status="confirmed",
                    original_text=data.get("original_text"),
                )
            )
        return len(trade_counts)

    if state.pending_intent in {"material_received", "material_issued"}:
        transaction_type = "received" if state.pending_intent == "material_received" else "issued"
        quantity = _decimal(data.get("quantity"))
        unit_symbol = data.get("unit") or "unit"
        material_name = data.get("material") or "Unspecified material"
        db.add(
            MaterialTransaction(
                company_id=project.company_id,
                project_id=project.id,
                entered_by=state.user_id,
                source_whatsapp_message_id=state.whatsapp_message_id,
                assistant_conversation_state_id=state.id,
                transaction_type=transaction_type,
                material_name=material_name,
                quantity=quantity,
                unit_symbol=unit_symbol,
                location_text=data.get("location"),
                transaction_date=work_date,
                status="confirmed",
                proof_status="not_attached",
                original_text=data.get("original_text"),
            )
        )
        _update_stock_balance(
            db=db,
            project=project,
            material_name=material_name,
            unit_symbol=unit_symbol,
            transaction_type=transaction_type,
            quantity=quantity,
        )
        return 1

    return 0


def _update_stock_balance(
    db: Session,
    project: Project,
    material_name: str,
    unit_symbol: str,
    transaction_type: str,
    quantity: Decimal,
) -> None:
    balance = db.scalar(
        select(MaterialStockBalance)
        .where(MaterialStockBalance.project_id == project.id)
        .where(MaterialStockBalance.material_name == material_name)
        .where(MaterialStockBalance.unit_symbol == unit_symbol)
    )
    if not balance:
        balance = MaterialStockBalance(
            company_id=project.company_id,
            project_id=project.id,
            material_name=material_name,
            unit_symbol=unit_symbol,
            total_received=Decimal("0"),
            total_issued=Decimal("0"),
            current_balance=Decimal("0"),
        )
        db.add(balance)

    if transaction_type == "received":
        balance.total_received += quantity
        balance.current_balance += quantity
    else:
        balance.total_issued += quantity
        balance.current_balance -= quantity
    balance.updated_at = datetime.utcnow()


def _decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _project_today(project: Project):
    try:
        timezone = ZoneInfo(project.timezone)
    except Exception:
        timezone = ZoneInfo("Asia/Kolkata")
    return datetime.now(timezone).date()
