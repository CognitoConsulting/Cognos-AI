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
    User,
    WhatsAppMessage,
    WhatsAppProviderAccount,
)
from app.schemas.assistant import AssistantConversationStateRead, AssistantParseResultRead
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
from app.services.whatsapp_provider import (
    find_provider_account_for_inbound,
    normalize_inbound_message,
    queue_outbound_text_message,
)

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
    user = _find_user_by_phone(db, normalized.phone)
    company_id = (
        user.company_id
        if user
        else provider_account.company_id
        if provider_account
        else None
    )
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
        raw_provider_payload=normalized.raw_payload,
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
