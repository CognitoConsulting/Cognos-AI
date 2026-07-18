from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import (
    AuthContext,
    get_auth_context,
    get_database_session,
    require_company_admin_access,
)
from app.models import (
    AssistantConversationState,
    AssistantParseResult,
    Company,
    MediaFile,
    ManpowerEntry,
    MaterialTransaction,
    Project,
    ProjectUser,
    ProgressEntry,
    User,
    VoiceNote,
    WhatsAppMessage,
    WhatsAppProviderAccount,
)
from app.schemas.assistant import AssistantConversationStateRead, AssistantParseResultRead
from app.schemas.reporting import VoiceNoteRead
from app.schemas.whatsapp import (
    WhatsAppMessageRead,
    WhatsAppOutboundTextCreate,
    WhatsAppProviderAccountCreate,
    WhatsAppProviderAccountRead,
    WhatsAppWebhookAccepted,
)
from app.services.assistant_parser import parse_message
from app.services.assistant_saver import (
    apply_missing_information_reply,
    apply_pending_confirmation_correction,
    is_affirmative_confirmation,
    save_latest_confirmed_update,
    save_project_selection_reply,
)
from app.services.assistant_workflow import build_conversation_decision
from app.services.media_storage import persist_inbound_media
from app.services.whatsapp_provider import (
    find_provider_account_for_inbound,
    normalize_inbound_message,
    queue_outbound_text_message,
)
from app.services.whatsapp_media import resolve_provider_media_url
from app.services.voice_transcription import is_voice_media_type, transcribe_voice_note

router = APIRouter()


@router.post(
    "/companies/{company_id}/whatsapp/provider-accounts",
    response_model=WhatsAppProviderAccountRead,
    status_code=status.HTTP_201_CREATED,
)
def create_provider_account(
    company_id: UUID,
    payload: WhatsAppProviderAccountCreate,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_database_session),
) -> WhatsAppProviderAccount:
    require_company_admin_access(db, company_id, auth)
    account_data = payload.model_dump()
    account_data["provider_name"] = account_data["provider_name"].strip().lower().replace("-", "_")
    account = WhatsAppProviderAccount(company_id=company_id, **account_data)
    db.add(account)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="WhatsApp provider account already exists for this company.",
        ) from exc
    db.refresh(account)
    return account


@router.get(
    "/companies/{company_id}/whatsapp/provider-accounts",
    response_model=list[WhatsAppProviderAccountRead],
)
def list_provider_accounts(
    company_id: UUID,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_database_session),
) -> list[WhatsAppProviderAccount]:
    require_company_admin_access(db, company_id, auth)
    return list(
        db.scalars(
            select(WhatsAppProviderAccount)
            .where(WhatsAppProviderAccount.company_id == company_id)
            .order_by(WhatsAppProviderAccount.created_at.desc())
        ).all()
    )


@router.get(
    "/companies/{company_id}/whatsapp/messages",
    response_model=list[WhatsAppMessageRead],
)
def list_whatsapp_messages(
    company_id: UUID,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_database_session),
) -> list[WhatsAppMessage]:
    require_company_admin_access(db, company_id, auth)
    return list(
        db.scalars(
            select(WhatsAppMessage)
            .where(WhatsAppMessage.company_id == company_id)
            .order_by(WhatsAppMessage.received_at.desc())
        ).all()
    )


@router.get(
    "/companies/{company_id}/whatsapp/voice-notes",
    response_model=list[VoiceNoteRead],
)
def list_voice_notes(
    company_id: UUID,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_database_session),
) -> list[VoiceNote]:
    require_company_admin_access(db, company_id, auth)
    return list(
        db.scalars(
            select(VoiceNote)
            .where(VoiceNote.company_id == company_id)
            .order_by(VoiceNote.created_at.desc())
        ).all()
    )


@router.post(
    "/companies/{company_id}/whatsapp/outbound-messages",
    response_model=WhatsAppMessageRead,
    status_code=status.HTTP_201_CREATED,
)
def create_outbound_whatsapp_message(
    company_id: UUID,
    payload: WhatsAppOutboundTextCreate,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_database_session),
) -> WhatsAppMessage:
    require_company_admin_access(db, company_id, auth)
    user = _require_company_user(db, company_id, payload.user_id) if payload.user_id else None
    result = queue_outbound_text_message(
        db=db,
        company_id=company_id,
        user_id=user.id if user else None,
        to_phone=payload.to_phone,
        message_text=payload.message_text,
        provider_name=payload.provider_name,
        provider_account_id=payload.provider_account_id,
        reason=payload.reason,
    )
    db.commit()
    db.refresh(result.message)
    return result.message


@router.get(
    "/companies/{company_id}/assistant/parse-results",
    response_model=list[AssistantParseResultRead],
)
def list_assistant_parse_results(
    company_id: UUID,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_database_session),
) -> list[AssistantParseResult]:
    require_company_admin_access(db, company_id, auth)
    return list(
        db.scalars(
            select(AssistantParseResult)
            .where(AssistantParseResult.company_id == company_id)
            .order_by(AssistantParseResult.created_at.desc())
        ).all()
    )


@router.get(
    "/companies/{company_id}/assistant/conversation-states",
    response_model=list[AssistantConversationStateRead],
)
def list_assistant_conversation_states(
    company_id: UUID,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_database_session),
) -> list[AssistantConversationState]:
    require_company_admin_access(db, company_id, auth)
    return list(
        db.scalars(
            select(AssistantConversationState)
            .where(AssistantConversationState.company_id == company_id)
            .order_by(AssistantConversationState.created_at.desc())
        ).all()
    )


@router.get("/webhooks/whatsapp/{provider_name}")
def verify_whatsapp_webhook(
    provider_name: str,
    request: Request,
) -> int | dict[str, str]:
    params = request.query_params
    challenge = params.get("hub.challenge")
    if challenge:
        return int(challenge)

    return {
        "status": "ok",
        "provider": provider_name,
        "detail": "Webhook verification endpoint is reachable.",
    }


@router.post(
    "/webhooks/whatsapp/{provider_name}",
    response_model=WhatsAppWebhookAccepted,
)
async def receive_whatsapp_webhook(
    provider_name: str,
    request: Request,
    db: Session = Depends(get_database_session),
) -> WhatsAppWebhookAccepted:
    payload = await request.json()
    normalized = normalize_inbound_message(provider_name, payload)
    if not normalized:
        return WhatsAppWebhookAccepted(
            status="ignored",
            message_id=None,
            processing_status="ignored",
            detail="No inbound user message found in provider payload.",
        )

    provider_account = find_provider_account_for_inbound(
        db,
        normalized.provider_name,
        normalized.provider_account_id,
    )
    provider_media_resolution = _resolve_provider_media_if_possible(
        normalized,
        provider_account,
    )
    user = _find_user_by_phone(db, normalized.phone)
    company_id = (
        user.company_id
        if user
        else provider_account.company_id
        if provider_account
        else None
    )
    stored_media_result = _persist_media_if_possible(normalized, company_id)
    processing_status = "received" if user else "unknown_user"

    message = WhatsAppMessage(
        company_id=company_id,
        user_id=user.id if user else None,
        phone=normalized.phone,
        direction="inbound",
        message_text=normalized.message_text,
        provider_name=normalized.provider_name,
        provider_message_id=normalized.provider_message_id,
        provider_account_id=normalized.provider_account_id,
        raw_provider_payload=_raw_provider_payload(
            normalized,
            provider_media_resolution,
            stored_media_result,
        ),
        processing_status=processing_status,
    )
    db.add(message)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = _find_existing_message(
            db,
            normalized.provider_name,
            normalized.provider_message_id,
        )
        if existing:
            return WhatsAppWebhookAccepted(
                status="duplicate",
                message_id=existing.id,
                processing_status=existing.processing_status,
                detail="Provider message was already received.",
            )
        raise

    db.refresh(message)

    if not user:
        _queue_assistant_reply(
            db,
            message,
            (
                "This WhatsApp number is not registered for Cognos AI yet. "
                "Please ask your company admin to add your user before sending site updates."
            )
            if message.company_id
            else None,
            reason="unknown_user",
        )
        db.commit()
        db.refresh(message)
        return WhatsAppWebhookAccepted(
            status="accepted",
            message_id=message.id,
            processing_status=message.processing_status,
            detail="Inbound WhatsApp message stored, but the user phone number is unknown.",
        )

    voice_result = _capture_voice_note_if_possible(db, user, message, normalized)
    if voice_result:
        message.raw_provider_payload = {
            **(message.raw_provider_payload or {}),
            "_cognos_voice": voice_result["audit_payload"],
        }
        if not voice_result.get("transcript_text"):
            message.processing_status = voice_result["processing_status"]
            _queue_assistant_reply(
                db,
                message,
                voice_result["reply_text"],
                reason="assistant_voice_capture",
            )
            db.commit()
            db.refresh(message)
            return WhatsAppWebhookAccepted(
                status="accepted",
                message_id=message.id,
                processing_status=message.processing_status,
                detail=voice_result["detail"],
            )

        message.message_text = voice_result["transcript_text"]
        db.flush()

    if not normalized.media_type:
        media_project_result = _save_pending_media_project_selection_reply(db, user, message)
        if media_project_result:
            message.processing_status = media_project_result["processing_status"]
            _queue_assistant_reply(
                db,
                message,
                media_project_result["reply_text"],
                reason="assistant_media_project_selection",
            )
            db.commit()
            db.refresh(message)
            return WhatsAppWebhookAccepted(
                status="accepted",
                message_id=message.id,
                processing_status=message.processing_status,
                detail=media_project_result["detail"],
            )

    media_result = _save_inbound_media_if_possible(db, user, message, normalized)
    if media_result:
        message.processing_status = media_result["processing_status"]
        _queue_assistant_reply(
            db,
            message,
            media_result["reply_text"],
            reason="assistant_media_capture",
        )
        db.commit()
        db.refresh(message)
        return WhatsAppWebhookAccepted(
            status="accepted",
            message_id=message.id,
            processing_status=message.processing_status,
            detail=media_result["detail"],
        )

    project_selection_result = save_project_selection_reply(
        db=db,
        user=user,
        project_selection_text=message.message_text,
    )
    if project_selection_result.handled:
        message.processing_status = project_selection_result.processing_status
        _queue_assistant_reply(
            db,
            message,
            project_selection_result.reply_text,
            reason="assistant_project_selection",
        )
        db.commit()
        db.refresh(message)
        return WhatsAppWebhookAccepted(
            status="accepted",
            message_id=message.id,
            processing_status=message.processing_status,
            detail=project_selection_result.detail,
        )

    missing_information_result = apply_missing_information_reply(
        db=db,
        user=user,
        missing_information_text=message.message_text,
    )
    if missing_information_result.handled:
        message.processing_status = missing_information_result.processing_status
        _queue_assistant_reply(
            db,
            message,
            missing_information_result.reply_text,
            reason="assistant_missing_information",
        )
        db.commit()
        db.refresh(message)
        return WhatsAppWebhookAccepted(
            status="accepted",
            message_id=message.id,
            processing_status=message.processing_status,
            detail=missing_information_result.detail,
        )

    correction_result = apply_pending_confirmation_correction(
        db=db,
        user=user,
        correction_message_text=message.message_text,
    )
    if correction_result.handled:
        message.processing_status = correction_result.processing_status
        _queue_assistant_reply(
            db,
            message,
            correction_result.reply_text,
            reason="assistant_correction",
        )
        db.commit()
        db.refresh(message)
        return WhatsAppWebhookAccepted(
            status="accepted",
            message_id=message.id,
            processing_status=message.processing_status,
            detail=correction_result.detail,
        )

    if is_affirmative_confirmation(message.message_text):
        save_result = save_latest_confirmed_update(
            db=db,
            user=user,
            confirmation_message_text=message.message_text,
        )
        if save_result.handled:
            message.processing_status = save_result.processing_status
            _queue_assistant_reply(
                db,
                message,
                save_result.reply_text,
                reason="assistant_confirmation",
            )
            db.commit()
            db.refresh(message)
            return WhatsAppWebhookAccepted(
                status="accepted",
                message_id=message.id,
                processing_status=message.processing_status,
                detail=save_result.detail,
            )

    parsed = parse_message(message.message_text)
    parse_result = AssistantParseResult(
        company_id=message.company_id,
        user_id=message.user_id,
        whatsapp_message_id=message.id,
        intent=parsed.intent,
        confidence=parsed.confidence,
        input_language=parsed.input_language,
        extracted_data=parsed.extracted_data,
        missing_fields=parsed.missing_fields,
        validation_status=parsed.validation_status,
        assistant_summary=parsed.assistant_summary,
        next_action=parsed.next_action,
    )
    db.add(parse_result)
    db.flush()

    decision = build_conversation_decision(parse_result, message.message_text)
    conversation_state = AssistantConversationState(
        company_id=message.company_id,
        user_id=message.user_id,
        whatsapp_message_id=message.id,
        parse_result_id=parse_result.id,
        status=decision.status,
        pending_intent=decision.pending_intent,
        pending_data=decision.pending_data,
        missing_fields=decision.missing_fields,
        confirmation_prompt=decision.confirmation_prompt,
        last_user_message=message.message_text,
    )
    db.add(conversation_state)
    message.processing_status = (
        decision.status if message.processing_status == "received" else message.processing_status
    )
    _queue_assistant_reply(
        db,
        message,
        decision.confirmation_prompt,
        reason="assistant_prompt",
    )
    db.commit()
    db.refresh(message)

    return WhatsAppWebhookAccepted(
        status="accepted",
        message_id=message.id,
        processing_status=message.processing_status,
        detail="Inbound WhatsApp message normalized, stored, and parsed.",
    )


def _require_company(db: Session, company_id: UUID) -> Company:
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )
    return company


def _require_company_user(db: Session, company_id: UUID, user_id: UUID) -> User:
    user = db.get(User, user_id)
    if not user or user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found for this company.",
        )
    return user


def _queue_assistant_reply(
    db: Session,
    inbound_message: WhatsAppMessage,
    reply_text: str | None,
    *,
    reason: str,
) -> None:
    if not reply_text or not inbound_message.company_id or not inbound_message.phone:
        return

    queue_outbound_text_message(
        db=db,
        company_id=inbound_message.company_id,
        user_id=inbound_message.user_id,
        to_phone=inbound_message.phone,
        message_text=reply_text,
        provider_name=inbound_message.provider_name,
        provider_account_id=inbound_message.provider_account_id,
        reason=reason,
    )


def _save_inbound_media_if_possible(
    db: Session,
    user: User,
    message: WhatsAppMessage,
    normalized,
) -> dict[str, str] | None:
    if not normalized.media_type:
        return None
    if is_voice_media_type(normalized.media_type):
        return None

    projects = _projects_available_to_user(db, user)
    if len(projects) == 0:
        return {
            "processing_status": "media_no_active_project",
            "detail": "Inbound media was received, but the user has no active project.",
            "reply_text": (
                "I received your image/proof, but I could not find an active project for your "
                "user. Please ask your company admin to assign you to a project."
            ),
        }

    if len(projects) > 1:
        return {
            "processing_status": "media_needs_project",
            "detail": "Inbound media was received, but project selection is required.",
            "reply_text": (
                "I received your image/proof, but I need to know which project it belongs to. "
                "Please reply with the project name or project code."
            ),
        }

    project = projects[0]
    link_target = _find_latest_linkable_entry(db, user, project, message)
    media_file = MediaFile(
        company_id=project.company_id,
        project_id=project.id,
        uploaded_by=user.id,
        source_whatsapp_message_id=message.id,
        linked_entity_type=link_target["entity_type"] if link_target else "whatsapp_message",
        linked_entity_id=link_target["entity_id"] if link_target else message.id,
        media_type=normalized.media_type,
        storage_url=_media_storage_url(normalized),
        file_name=normalized.media_file_name,
        caption=normalized.media_caption or message.message_text,
        provider_media_id=normalized.provider_media_id,
        processing_status=_media_processing_status(normalized),
        captured_at=message.received_at,
    )
    db.add(media_file)
    _mark_linked_entry_has_proof(link_target)
    link_text = (
        f" and linked it to the latest {link_target['label']} entry"
        if link_target
        else ""
    )
    return {
        "processing_status": "media_stored",
        "detail": "Inbound WhatsApp media was stored as a project media/proof record.",
        "reply_text": (
            f"Received and stored this {normalized.media_type} proof for {project.name}{link_text}."
        ),
    }


def _save_pending_media_project_selection_reply(
    db: Session,
    user: User,
    message: WhatsAppMessage,
) -> dict[str, str] | None:
    if not message.message_text:
        return None

    pending_media_message = _find_latest_pending_media_message(db, user)
    if not pending_media_message:
        return None

    match_result = _match_project_from_text(db, user, message.message_text)
    if match_result["status"] == "no_match":
        return {
            "processing_status": "media_needs_project",
            "detail": "Media project selection reply did not match an active project.",
            "reply_text": (
                "I could not match that to one of your active projects. "
                "Please send the project name or project code for the image/proof."
            ),
        }

    if match_result["status"] == "ambiguous":
        return {
            "processing_status": "media_needs_project",
            "detail": "Media project selection reply matched more than one project.",
            "reply_text": (
                "I found more than one matching project. Please send the exact project code "
                "for the image/proof."
            ),
        }

    project = match_result["project"]
    media_file = _create_media_file_from_pending_message(
        db=db,
        user=user,
        pending_media_message=pending_media_message,
        project=project,
    )
    pending_media_message.processing_status = "media_stored"
    message.raw_provider_payload = {
        **(message.raw_provider_payload or {}),
        "_cognos_media_project_selection": {
            "pending_media_message_id": str(pending_media_message.id),
            "media_file_id": str(media_file.id),
            "project_id": str(project.id),
        },
    }
    return {
        "processing_status": "media_project_selected",
        "detail": "Media project selection received and image/proof stored.",
        "reply_text": (
            f"Received. I stored the image/proof for {project.name}"
            f"{_media_link_reply_suffix(media_file)}."
        ),
    }


def _find_latest_pending_media_message(db: Session, user: User) -> WhatsAppMessage | None:
    pending_messages = list(
        db.scalars(
            select(WhatsAppMessage)
            .where(WhatsAppMessage.company_id == user.company_id)
            .where(WhatsAppMessage.user_id == user.id)
            .where(WhatsAppMessage.direction == "inbound")
            .where(WhatsAppMessage.processing_status == "media_needs_project")
            .order_by(WhatsAppMessage.received_at.desc())
            .limit(10)
        ).all()
    )
    for pending_message in pending_messages:
        if (pending_message.raw_provider_payload or {}).get("_cognos_media"):
            return pending_message
    return None


def _create_media_file_from_pending_message(
    db: Session,
    user: User,
    pending_media_message: WhatsAppMessage,
    project: Project,
) -> MediaFile:
    media_payload = (pending_media_message.raw_provider_payload or {}).get("_cognos_media") or {}
    link_target = _find_latest_linkable_entry(db, user, project, pending_media_message)
    media_file = MediaFile(
        company_id=project.company_id,
        project_id=project.id,
        uploaded_by=user.id,
        source_whatsapp_message_id=pending_media_message.id,
        linked_entity_type=link_target["entity_type"] if link_target else "whatsapp_message",
        linked_entity_id=link_target["entity_id"] if link_target else pending_media_message.id,
        media_type=media_payload.get("media_type") or "image",
        storage_url=_media_storage_url_from_payload(
            pending_media_message.provider_name,
            media_payload,
        ),
        file_name=media_payload.get("media_file_name"),
        caption=media_payload.get("media_caption") or pending_media_message.message_text,
        provider_media_id=media_payload.get("provider_media_id"),
        processing_status="stored"
        if media_payload.get("stored_media_url") or media_payload.get("media_url")
        else "provider_reference",
        captured_at=pending_media_message.received_at,
    )
    db.add(media_file)
    _mark_linked_entry_has_proof(link_target)
    db.flush()
    return media_file


def _find_latest_linkable_entry(
    db: Session,
    user: User,
    project: Project,
    media_message: WhatsAppMessage,
) -> dict | None:
    if not media_message.received_at:
        return None

    cutoff = media_message.received_at - timedelta(minutes=30)
    candidates = [
        _latest_progress_entry(db, user, project, cutoff, media_message.received_at),
        _latest_manpower_entry(db, user, project, cutoff, media_message.received_at),
        _latest_material_transaction(db, user, project, cutoff, media_message.received_at),
    ]
    candidates = [candidate for candidate in candidates if candidate]
    if not candidates:
        return None
    return max(candidates, key=lambda candidate: candidate["created_at"])


def _latest_progress_entry(
    db: Session,
    user: User,
    project: Project,
    cutoff,
    received_at,
) -> dict | None:
    entry = db.scalar(
        select(ProgressEntry)
        .where(ProgressEntry.company_id == project.company_id)
        .where(ProgressEntry.project_id == project.id)
        .where(ProgressEntry.entered_by == user.id)
        .where(ProgressEntry.created_at >= cutoff)
        .where(ProgressEntry.created_at <= received_at)
        .order_by(ProgressEntry.created_at.desc())
    )
    if not entry:
        return None
    return {
        "entity": entry,
        "entity_type": "progress_entry",
        "entity_id": entry.id,
        "label": "progress",
        "created_at": entry.created_at,
    }


def _latest_manpower_entry(
    db: Session,
    user: User,
    project: Project,
    cutoff,
    received_at,
) -> dict | None:
    entry = db.scalar(
        select(ManpowerEntry)
        .where(ManpowerEntry.company_id == project.company_id)
        .where(ManpowerEntry.project_id == project.id)
        .where(ManpowerEntry.entered_by == user.id)
        .where(ManpowerEntry.created_at >= cutoff)
        .where(ManpowerEntry.created_at <= received_at)
        .order_by(ManpowerEntry.created_at.desc())
    )
    if not entry:
        return None
    return {
        "entity": entry,
        "entity_type": "manpower_entry",
        "entity_id": entry.id,
        "label": "manpower",
        "created_at": entry.created_at,
    }


def _latest_material_transaction(
    db: Session,
    user: User,
    project: Project,
    cutoff,
    received_at,
) -> dict | None:
    entry = db.scalar(
        select(MaterialTransaction)
        .where(MaterialTransaction.company_id == project.company_id)
        .where(MaterialTransaction.project_id == project.id)
        .where(MaterialTransaction.entered_by == user.id)
        .where(MaterialTransaction.created_at >= cutoff)
        .where(MaterialTransaction.created_at <= received_at)
        .order_by(MaterialTransaction.created_at.desc())
    )
    if not entry:
        return None
    return {
        "entity": entry,
        "entity_type": "material_transaction",
        "entity_id": entry.id,
        "label": "material",
        "created_at": entry.created_at,
    }


def _mark_linked_entry_has_proof(link_target: dict | None) -> None:
    if not link_target or link_target["entity_type"] != "material_transaction":
        return
    link_target["entity"].proof_status = "attached"


def _media_link_reply_suffix(media_file: MediaFile) -> str:
    labels = {
        "progress_entry": " and linked it to the latest progress entry",
        "manpower_entry": " and linked it to the latest manpower entry",
        "material_transaction": " and linked it to the latest material entry",
    }
    return labels.get(media_file.linked_entity_type or "", "")


def _media_storage_url_from_payload(provider_name: str, media_payload: dict) -> str:
    if media_payload.get("stored_media_url"):
        return media_payload["stored_media_url"]
    if media_payload.get("media_url"):
        return media_payload["media_url"]
    return f"provider://{provider_name}/{media_payload.get('provider_media_id') or 'media'}"


def _media_storage_url(normalized) -> str:
    if normalized.stored_media_url:
        return normalized.stored_media_url
    if _media_has_storable_url(normalized):
        return normalized.media_url
    return f"provider://{normalized.provider_name}/{normalized.provider_media_id or 'media'}"


def _normalized_media_audit_payload(normalized) -> dict[str, str | None]:
    return {
        "media_type": normalized.media_type,
        "media_url": normalized.media_url if _media_has_storable_url(normalized) else None,
        "media_url_status": "runtime_only" if normalized.media_download_headers else None,
        "stored_media_url": normalized.stored_media_url,
        "stored_media_status": normalized.stored_media_status,
        "stored_media_error": normalized.stored_media_error,
        "media_file_name": normalized.media_file_name,
        "provider_media_id": normalized.provider_media_id,
        "media_caption": normalized.media_caption,
        "media_mime_type": normalized.media_mime_type,
        "transcription_text": normalized.transcription_text,
    }


def _media_has_storable_url(normalized) -> bool:
    return bool(normalized.media_url and not normalized.media_download_headers)


def _media_processing_status(normalized) -> str:
    if normalized.stored_media_url:
        return "stored"
    if _media_has_storable_url(normalized):
        return "stored_external_url"
    if normalized.stored_media_status:
        return normalized.stored_media_status
    return "provider_reference"


def _raw_provider_payload(normalized, provider_media_resolution, stored_media_result) -> dict:
    if not normalized.media_type:
        return normalized.raw_payload

    payload = {
        **normalized.raw_payload,
        "_cognos_media": _normalized_media_audit_payload(normalized),
    }
    if provider_media_resolution:
        payload["_cognos_provider_media_resolution"] = {
            **(provider_media_resolution.audit_payload or {}),
            "status": provider_media_resolution.status,
            "error_message": provider_media_resolution.error_message,
        }
    if stored_media_result:
        payload["_cognos_media_storage"] = {
            **(stored_media_result.audit_payload or {}),
            "status": stored_media_result.status,
            "error_message": stored_media_result.error_message,
        }
    return payload


def _resolve_provider_media_if_possible(normalized, provider_account):
    if not normalized.media_type:
        return None

    resolution = resolve_provider_media_url(normalized, provider_account)
    if resolution.media_url:
        normalized.media_url = resolution.media_url
    if resolution.mime_type and not normalized.media_mime_type:
        normalized.media_mime_type = resolution.mime_type
    if resolution.download_headers:
        normalized.media_download_headers = resolution.download_headers
    return resolution


def _persist_media_if_possible(normalized, company_id):
    if not normalized.media_type:
        return None

    result = persist_inbound_media(normalized, company_id=company_id)
    normalized.stored_media_url = result.storage_url
    normalized.stored_media_status = result.status
    normalized.stored_media_error = result.error_message
    if result.mime_type and not normalized.media_mime_type:
        normalized.media_mime_type = result.mime_type
    if result.file_name and not normalized.media_file_name:
        normalized.media_file_name = result.file_name
    return result


def _capture_voice_note_if_possible(
    db: Session,
    user: User,
    message: WhatsAppMessage,
    normalized,
) -> dict | None:
    if not is_voice_media_type(normalized.media_type):
        return None

    company = db.get(Company, user.company_id)
    transcription = transcribe_voice_note(normalized, company)
    project = _single_project_available_to_user(db, user)
    voice_note = VoiceNote(
        company_id=user.company_id,
        project_id=project.id if project else None,
        uploaded_by=user.id,
        source_whatsapp_message_id=message.id,
        storage_url=_media_storage_url(normalized),
        file_name=normalized.media_file_name,
        provider_media_id=normalized.provider_media_id,
        mime_type=normalized.media_mime_type,
        transcription_status=transcription.status,
        transcription_provider=transcription.provider_name,
        transcript_text=transcription.transcript_text,
        transcript_language=transcription.language,
        error_message=transcription.error_message,
        captured_at=message.received_at,
    )
    db.add(voice_note)
    db.flush()

    audit_payload = {
        "voice_note_id": str(voice_note.id),
        "transcription_status": transcription.status,
        "transcription_provider": transcription.provider_name,
        "transcript_available": bool(transcription.transcript_text),
    }

    if transcription.transcript_text:
        return {
            "processing_status": "voice_transcribed",
            "detail": "Inbound WhatsApp voice note was stored, transcribed, and sent to the assistant workflow.",
            "transcript_text": transcription.transcript_text,
            "audit_payload": audit_payload,
        }

    return {
        "processing_status": f"voice_{transcription.status}",
        "detail": "Inbound WhatsApp voice note was stored, but no transcript was available.",
        "reply_text": _voice_transcription_unavailable_reply(transcription.status),
        "audit_payload": audit_payload,
    }


def _single_project_available_to_user(db: Session, user: User) -> Project | None:
    projects = _projects_available_to_user(db, user)
    return projects[0] if len(projects) == 1 else None


def _voice_transcription_unavailable_reply(status: str) -> str:
    if status == "unsupported_format":
        return (
            "Received your voice note, but this audio format needs conversion before I can "
            "transcribe it. Please type the update for now so I can record it."
        )
    if status == "media_unavailable":
        return (
            "Received your voice note, but I only received the provider media reference, not a "
            "downloadable audio file. Please type the update for now so I can record it."
        )
    if status in {"platform_key_not_configured", "company_key_not_configured", "not_configured"}:
        return (
            "Received your voice note, but voice transcription is not configured yet. "
            "Please type the update for now, or ask your admin to enable voice transcription."
        )
    if status == "download_failed":
        return (
            "Received your voice note, but I could not download the audio for transcription. "
            "Please type the update for now so I can record it."
        )
    if status == "transcription_failed":
        return (
            "Received your voice note, but transcription failed. Please type the update for now "
            "so I can record it."
        )
    return (
        "Received your voice note. I have stored it for audit, but transcription is not ready yet. "
        "Please type the update for now so I can record it."
    )


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


def _match_project_from_text(db: Session, user: User, project_selection_text: str) -> dict:
    text = _normalize_project_text(project_selection_text)
    if not text:
        return {"status": "no_match", "project": None}

    projects = _projects_available_to_user(db, user)
    exact_matches = [
        project
        for project in projects
        if text in {_normalize_project_text(project.code), _normalize_project_text(project.name)}
    ]
    if len(exact_matches) == 1:
        return {"status": "matched", "project": exact_matches[0]}
    if len(exact_matches) > 1:
        return {"status": "ambiguous", "project": None}

    partial_matches = [
        project
        for project in projects
        if _project_text_matches(text, project.name) or _project_text_matches(text, project.code)
    ]
    if len(partial_matches) == 1:
        return {"status": "matched", "project": partial_matches[0]}
    if len(partial_matches) > 1:
        return {"status": "ambiguous", "project": None}

    return {"status": "no_match", "project": None}


def _project_text_matches(text: str, candidate: str | None) -> bool:
    candidate_text = _normalize_project_text(candidate)
    return bool(candidate_text and (text in candidate_text or candidate_text in text))


def _normalize_project_text(value: str | None) -> str:
    return " ".join((value or "").strip().lower().replace("-", " ").split())


def _find_user_by_phone(db: Session, phone: str | None) -> User | None:
    if not phone:
        return None
    return db.scalar(select(User).where(User.phone == phone).where(User.is_active.is_(True)))


def _find_existing_message(
    db: Session,
    provider_name: str,
    provider_message_id: str | None,
) -> WhatsAppMessage | None:
    if not provider_message_id:
        return None
    return db.scalar(
        select(WhatsAppMessage)
        .where(WhatsAppMessage.provider_name == provider_name)
        .where(WhatsAppMessage.provider_message_id == provider_message_id)
    )
