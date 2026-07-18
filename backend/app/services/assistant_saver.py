from __future__ import annotations

import re
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

CORRECTION_TERMS = {
    "change",
    "correct",
    "correction",
    "update",
    "replace",
    "actually",
    "instead",
    "galat",
    "sahi",
    "badal",
}

CORRECTION_FIELD_TERMS = {
    "qty",
    "quantity",
    "unit",
    "location",
    "area",
    "material",
    "activity",
    "trade",
    "worker",
    "workers",
    "mason",
    "helper",
    "labour",
    "labor",
    "mazdoor",
    "electrician",
    "plumber",
    "carpenter",
    "painter",
}

UNIT_TERMS = {
    "sqm",
    "sqft",
    "cum",
    "bags",
    "bag",
    "kg",
    "ton",
    "tons",
    "nos",
    "pieces",
}

TRADE_TERMS = {
    "mason",
    "helper",
    "labour",
    "labor",
    "mazdoor",
    "electrician",
    "plumber",
    "carpenter",
    "painter",
}


@dataclass(frozen=True)
class ConfirmationSaveResult:
    handled: bool
    processing_status: str
    detail: str
    saved_record_type: str | None = None
    saved_record_count: int = 0
    reply_text: str | None = None


def is_affirmative_confirmation(message_text: str | None) -> bool:
    normalized = (message_text or "").strip().lower().strip(".! ")
    return normalized in AFFIRMATIVE_REPLIES


def apply_pending_confirmation_correction(
    db: Session,
    user: User,
    correction_message_text: str | None,
) -> ConfirmationSaveResult:
    pending_state = _find_latest_pending_confirmation(db, user)
    if not pending_state:
        return ConfirmationSaveResult(
            handled=False,
            processing_status="no_pending_confirmation",
            detail="No pending assistant confirmation was found for this user.",
        )

    correction = _extract_correction(
        pending_state.pending_intent,
        pending_state.pending_data or {},
        correction_message_text,
    )
    if not correction:
        return ConfirmationSaveResult(
            handled=False,
            processing_status="no_correction_detected",
            detail="No correction fields were detected in this reply.",
        )

    pending_data = dict(pending_state.pending_data or {})
    pending_data.update(correction)
    pending_state.pending_data = pending_data
    pending_state.last_user_message = correction_message_text
    pending_state.confirmation_prompt = _build_corrected_confirmation_prompt(
        pending_state.pending_intent,
        pending_data,
    )
    pending_state.updated_at = datetime.utcnow()
    db.commit()

    return ConfirmationSaveResult(
        handled=True,
        processing_status="awaiting_confirmation_corrected",
        detail="Assistant confirmation was corrected and is waiting for confirmation again.",
        reply_text=pending_state.confirmation_prompt,
    )


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
            reply_text=pending_state.confirmation_prompt,
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
            reply_text=pending_state.confirmation_prompt,
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
            reply_text=pending_state.confirmation_prompt,
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
            reply_text=pending_state.confirmation_prompt,
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
        reply_text=pending_state.confirmation_prompt,
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


def _extract_correction(
    intent: str,
    pending_data: dict,
    message_text: str | None,
) -> dict | None:
    text = (message_text or "").strip()
    lowered = text.lower()
    if not text or not _looks_like_correction(lowered):
        return None

    correction: dict = {}
    quantity, unit = _extract_quantity_and_unit(lowered)
    if intent in {"progress", "material_received", "material_issued"}:
        if quantity is not None:
            correction["quantity"] = quantity
        if unit:
            correction["unit"] = unit
        else:
            unit_only = _extract_unit_only(lowered)
            if unit_only:
                correction["unit"] = unit_only

    if intent in {"progress", "material_received", "material_issued"}:
        activity = _extract_named_value(text, ["activity", "work", "kaam"])
        material = _extract_named_value(text, ["material"])
        if activity and intent == "progress":
            correction["activity"] = activity
        if material and intent in {"material_received", "material_issued"}:
            correction["material"] = material

    location = _extract_named_value(text, ["location", "area", "site"])
    if not location:
        location = _extract_location(text)
    if location:
        correction["location"] = location

    if intent == "manpower":
        trade_counts = _extract_trade_counts(lowered)
        if trade_counts:
            existing_counts = dict(pending_data.get("trade_counts") or {})
            existing_counts.update(trade_counts)
            correction["trade_counts"] = existing_counts

    if not correction:
        return None
    return correction


def _looks_like_correction(lowered: str) -> bool:
    if any(term in lowered for term in CORRECTION_TERMS):
        return True
    if any(term in lowered for term in CORRECTION_FIELD_TERMS):
        return True
    quantity, unit = _extract_quantity_and_unit(lowered)
    return bool(quantity is not None and unit and len(lowered.split()) <= 4)


def _extract_quantity_and_unit(lowered: str) -> tuple[float | None, str | None]:
    unit_pattern = "|".join(sorted(UNIT_TERMS, key=len, reverse=True))
    quantity_with_unit = re.search(rf"\b(\d+(?:\.\d+)?)\s*({unit_pattern})\b", lowered)
    if quantity_with_unit:
        return float(quantity_with_unit.group(1)), quantity_with_unit.group(2)

    quantity = re.search(
        r"\b(?:qty|quantity|change quantity to|quantity to|make it|actually)\s*(?:is|to|=)?\s*(\d+(?:\.\d+)?)\b",
        lowered,
    )
    unit = re.search(rf"\b(?:unit|in)\s*(?:is|to|=)?\s*({unit_pattern})\b", lowered)
    if quantity:
        return float(quantity.group(1)), unit.group(1) if unit else None

    loose_number = re.search(r"\b(\d+(?:\.\d+)?)\b", lowered)
    return (float(loose_number.group(1)), unit.group(1) if unit else None) if loose_number else (None, None)


def _extract_unit_only(lowered: str) -> str | None:
    unit_pattern = "|".join(sorted(UNIT_TERMS, key=len, reverse=True))
    match = re.search(rf"\b(?:unit|in)\s*(?:is|to|=)?\s*({unit_pattern})\b", lowered)
    return match.group(1) if match else None


def _extract_named_value(text: str, labels: list[str]) -> str | None:
    label_pattern = "|".join(re.escape(label) for label in labels)
    match = re.search(
        rf"\b(?:{label_pattern})\s*(?:is|to|=|:)?\s*([A-Za-z0-9][A-Za-z0-9 /-]{{1,80}})",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    value = re.split(r"\b(?:and|with|qty|quantity|unit|location|area)\b", match.group(1), flags=re.IGNORECASE)[0]
    return value.strip(" .,!") or None


def _extract_location(text: str) -> str | None:
    patterns = [
        r"((?:Tower|Block)\s+[A-Z0-9]+(?:\s+Floor\s+\d+)?)",
        r"(Floor\s+\d+)",
        r"(Basement(?:\s+\d+)?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _extract_trade_counts(lowered: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for trade in TRADE_TERMS:
        match = re.search(rf"\b(?:{re.escape(trade)}s?)\s*(?:is|to|=)?\s*(\d+)\b", lowered)
        if not match:
            match = re.search(rf"\b(\d+)\s+{re.escape(trade)}s?\b", lowered)
        if match:
            count_group = 1 if match.lastindex == 1 else 1
            counts[trade] = int(match.group(count_group))
    return counts


def _build_corrected_confirmation_prompt(intent: str, pending_data: dict) -> str:
    return (
        f"I have updated the {intent.replace('_', ' ')} entry:\n"
        f"{_summarize_pending_data(pending_data)}\n\n"
        "Please reply Yes to save this corrected entry, or tell me what else to change."
    )


def _summarize_pending_data(pending_data: dict) -> str:
    details = []
    for key, value in pending_data.items():
        if key == "original_text" or value in [None, {}, []]:
            continue
        if isinstance(value, dict):
            nested = ", ".join(f"{nested_key}: {nested_value}" for nested_key, nested_value in value.items())
            details.append(f"{key.replace('_', ' ')}: {nested}")
        else:
            details.append(f"{key.replace('_', ' ')}: {value}")
    return "; ".join(details) if details else "No structured details found yet."


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
