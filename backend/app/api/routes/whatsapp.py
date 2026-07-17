from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_database_session, require_platform_admin
from app.models import (
    AssistantParseResult,
    Company,
    User,
    WhatsAppMessage,
    WhatsAppProviderAccount,
)
from app.schemas.assistant import AssistantParseResultRead
from app.schemas.whatsapp import (
    WhatsAppMessageRead,
    WhatsAppProviderAccountCreate,
    WhatsAppProviderAccountRead,
    WhatsAppWebhookAccepted,
)
from app.services.whatsapp_provider import normalize_inbound_message
from app.services.assistant_parser import parse_message

router = APIRouter()


@router.post(
    "/companies/{company_id}/whatsapp/provider-accounts",
    response_model=WhatsAppProviderAccountRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_platform_admin)],
)
def create_provider_account(
    company_id: UUID,
    payload: WhatsAppProviderAccountCreate,
    db: Session = Depends(get_database_session),
) -> WhatsAppProviderAccount:
    _require_company(db, company_id)
    account = WhatsAppProviderAccount(company_id=company_id, **payload.model_dump())
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
    dependencies=[Depends(require_platform_admin)],
)
def list_provider_accounts(
    company_id: UUID,
    db: Session = Depends(get_database_session),
) -> list[WhatsAppProviderAccount]:
    _require_company(db, company_id)
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
    dependencies=[Depends(require_platform_admin)],
)
def list_whatsapp_messages(
    company_id: UUID,
    db: Session = Depends(get_database_session),
) -> list[WhatsAppMessage]:
    _require_company(db, company_id)
    return list(
        db.scalars(
            select(WhatsAppMessage)
            .where(WhatsAppMessage.company_id == company_id)
            .order_by(WhatsAppMessage.received_at.desc())
        ).all()
    )


@router.get(
    "/companies/{company_id}/assistant/parse-results",
    response_model=list[AssistantParseResultRead],
    dependencies=[Depends(require_platform_admin)],
)
def list_assistant_parse_results(
    company_id: UUID,
    db: Session = Depends(get_database_session),
) -> list[AssistantParseResult]:
    _require_company(db, company_id)
    return list(
        db.scalars(
            select(AssistantParseResult)
            .where(AssistantParseResult.company_id == company_id)
            .order_by(AssistantParseResult.created_at.desc())
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

    user = _find_user_by_phone(db, normalized.phone)
    company_id = user.company_id if user else None
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
    message.processing_status = (
        "parsed" if message.processing_status == "received" else message.processing_status
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
