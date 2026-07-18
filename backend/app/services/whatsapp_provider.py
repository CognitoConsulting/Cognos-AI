from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import WhatsAppMessage, WhatsAppProviderAccount


@dataclass
class NormalizedInboundMessage:
    provider_name: str
    provider_message_id: str | None
    provider_account_id: str | None
    phone: str | None
    message_text: str | None
    media_type: str | None
    media_url: str | None
    media_file_name: str | None
    provider_media_id: str | None
    media_caption: str | None
    raw_payload: dict[str, Any]


@dataclass(frozen=True)
class OutboundWhatsAppResult:
    message: WhatsAppMessage
    delivery_mode: str
    detail: str


def normalize_inbound_message(
    provider_name: str,
    payload: dict[str, Any],
) -> NormalizedInboundMessage | None:
    normalized_provider = provider_name.strip().lower().replace("-", "_")

    if normalized_provider in {"meta", "meta_cloud_api", "whatsapp_cloud_api"}:
        return _normalize_meta_payload(normalized_provider, payload)

    if normalized_provider in {"generic", "test"}:
        return _normalize_generic_payload(normalized_provider, payload)

    return _normalize_generic_payload(normalized_provider, payload)


def find_provider_account_for_inbound(
    db: Session,
    provider_name: str,
    provider_account_id: str | None,
) -> WhatsAppProviderAccount | None:
    if not provider_account_id:
        return None

    normalized_provider = _normalize_provider_name(provider_name)
    query = (
        select(WhatsAppProviderAccount)
        .where(WhatsAppProviderAccount.provider_name == normalized_provider)
        .where(WhatsAppProviderAccount.status == "active")
    )
    query = query.where(
        or_(
            WhatsAppProviderAccount.provider_account_id == provider_account_id,
            WhatsAppProviderAccount.phone_number_id == provider_account_id,
        )
    )

    return db.scalar(query.order_by(WhatsAppProviderAccount.created_at.desc()))


def queue_outbound_text_message(
    db: Session,
    *,
    company_id,
    to_phone: str | None,
    message_text: str,
    user_id=None,
    provider_name: str | None = None,
    provider_account_id: str | None = None,
    reason: str = "assistant_reply",
) -> OutboundWhatsAppResult:
    """Create the auditable outbound WhatsApp message record.

    Generic/test providers are treated as local simulated sends so the MVP can be
    tested without WhatsApp credentials. Real providers are queued until a
    provider-specific sender is configured.
    """
    account = _select_outbound_account(
        db=db,
        company_id=company_id,
        provider_name=provider_name,
        provider_account_id=provider_account_id,
    )
    resolved_provider = (
        account.provider_name if account else _normalize_provider_name(provider_name or "generic")
    )
    resolved_provider_account_id = (
        account.provider_account_id or account.phone_number_id if account else provider_account_id
    )
    delivery_mode = "simulated" if resolved_provider in {"generic", "test"} else "queued"
    processing_status = "sent" if delivery_mode == "simulated" else "queued"
    provider_message_id = (
        f"local-out-{uuid4()}" if delivery_mode == "simulated" else None
    )

    raw_payload = {
        "to": to_phone,
        "type": "text",
        "text": {"body": message_text},
        "reason": reason,
        "delivery_mode": delivery_mode,
    }
    if delivery_mode == "queued":
        raw_payload["note"] = (
            "Provider-specific outbound delivery is not configured yet. "
            "This message is logged for audit and future delivery processing."
        )

    message = WhatsAppMessage(
        company_id=company_id,
        user_id=user_id,
        phone=to_phone,
        direction="outbound",
        message_text=message_text,
        provider_name=resolved_provider,
        provider_message_id=provider_message_id,
        provider_account_id=resolved_provider_account_id,
        raw_provider_payload=raw_payload,
        processing_status=processing_status,
    )
    db.add(message)
    return OutboundWhatsAppResult(
        message=message,
        delivery_mode=delivery_mode,
        detail=(
            "Outbound WhatsApp message simulated and logged."
            if delivery_mode == "simulated"
            else "Outbound WhatsApp message queued and logged."
        ),
    )


def _normalize_generic_payload(
    provider_name: str,
    payload: dict[str, Any],
) -> NormalizedInboundMessage | None:
    message_text = _first_text(
        payload.get("message_text"),
        payload.get("text"),
        payload.get("body"),
        payload.get("message", {}).get("text") if isinstance(payload.get("message"), dict) else None,
    )
    phone = _first_text(
        payload.get("phone"),
        payload.get("from"),
        payload.get("wa_id"),
        payload.get("sender"),
    )
    provider_message_id = _first_text(
        payload.get("provider_message_id"),
        payload.get("message_id"),
        payload.get("id"),
    )
    provider_account_id = _first_text(
        payload.get("provider_account_id"),
        payload.get("phone_number_id"),
        payload.get("account_id"),
    )
    media_type = _first_text(
        payload.get("media_type"),
        payload.get("type") if payload.get("type") in {"image", "photo", "video", "document"} else None,
    )
    media_url = _first_text(
        payload.get("media_url"),
        payload.get("storage_url"),
        payload.get("url"),
        payload.get("image_url"),
    )
    provider_media_id = _first_text(
        payload.get("provider_media_id"),
        payload.get("media_id"),
        payload.get("image_id"),
    )
    media_caption = _first_text(
        payload.get("caption"),
        payload.get("media_caption"),
    )
    media_file_name = _first_text(
        payload.get("file_name"),
        payload.get("filename"),
    )

    if not any([message_text, phone, provider_message_id, media_url, provider_media_id]):
        return None

    return NormalizedInboundMessage(
        provider_name=_normalize_provider_name(provider_name),
        provider_message_id=provider_message_id,
        provider_account_id=provider_account_id,
        phone=phone,
        message_text=message_text,
        media_type=_normalize_media_type(media_type, media_url, provider_media_id),
        media_url=media_url,
        media_file_name=media_file_name,
        provider_media_id=provider_media_id,
        media_caption=media_caption,
        raw_payload=payload,
    )


def _normalize_meta_payload(
    provider_name: str,
    payload: dict[str, Any],
) -> NormalizedInboundMessage | None:
    try:
        entry = payload["entry"][0]
        change = entry["changes"][0]
        value = change["value"]
    except (KeyError, IndexError, TypeError):
        return _normalize_generic_payload(provider_name, payload)

    metadata = value.get("metadata", {})
    provider_account_id = _first_text(
        metadata.get("phone_number_id"),
        metadata.get("display_phone_number"),
    )

    messages = value.get("messages") or []
    if not messages:
        return None

    message = messages[0]
    message_type = message.get("type")
    text_body = None
    media_type = None
    media_url = None
    provider_media_id = None
    media_caption = None
    media_file_name = None
    if message_type == "text":
        text_body = (message.get("text") or {}).get("body")
    elif message_type in {"button", "interactive"}:
        text_body = _extract_interactive_text(message)
    elif message_type in {"image", "video", "document"}:
        media_payload = message.get(message_type) or {}
        media_type = message_type
        provider_media_id = _first_text(media_payload.get("id"))
        media_caption = _first_text(media_payload.get("caption"))
        media_file_name = _first_text(media_payload.get("filename"))
        media_url = _first_text(media_payload.get("link"), media_payload.get("url"))

    return NormalizedInboundMessage(
        provider_name=_normalize_provider_name(provider_name),
        provider_message_id=_first_text(message.get("id")),
        provider_account_id=provider_account_id,
        phone=_first_text(message.get("from")),
        message_text=_first_text(text_body),
        media_type=_normalize_media_type(media_type, media_url, provider_media_id),
        media_url=media_url,
        media_file_name=media_file_name,
        provider_media_id=provider_media_id,
        media_caption=media_caption,
        raw_payload=payload,
    )


def _extract_interactive_text(message: dict[str, Any]) -> str | None:
    if "button" in message and isinstance(message["button"], dict):
        return _first_text(message["button"].get("text"), message["button"].get("payload"))

    interactive = message.get("interactive")
    if not isinstance(interactive, dict):
        return None

    button_reply = interactive.get("button_reply")
    if isinstance(button_reply, dict):
        return _first_text(button_reply.get("title"), button_reply.get("id"))

    list_reply = interactive.get("list_reply")
    if isinstance(list_reply, dict):
        return _first_text(list_reply.get("title"), list_reply.get("id"))

    return None


def _first_text(*values: Any) -> str | None:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _select_outbound_account(
    db: Session,
    *,
    company_id,
    provider_name: str | None,
    provider_account_id: str | None,
) -> WhatsAppProviderAccount | None:
    normalized_provider = _normalize_provider_name(provider_name or "")
    query = (
        select(WhatsAppProviderAccount)
        .where(WhatsAppProviderAccount.company_id == company_id)
        .where(WhatsAppProviderAccount.status == "active")
    )
    if normalized_provider:
        query = query.where(WhatsAppProviderAccount.provider_name == normalized_provider)
    if provider_account_id:
        query = query.where(
            or_(
                WhatsAppProviderAccount.provider_account_id == provider_account_id,
                WhatsAppProviderAccount.phone_number_id == provider_account_id,
            )
        )

    account = db.scalar(query.order_by(WhatsAppProviderAccount.created_at.desc()))
    if account or normalized_provider or provider_account_id:
        return account

    return db.scalar(
        select(WhatsAppProviderAccount)
        .where(WhatsAppProviderAccount.company_id == company_id)
        .where(WhatsAppProviderAccount.status == "active")
        .order_by(WhatsAppProviderAccount.created_at.desc())
    )


def _normalize_provider_name(provider_name: str) -> str:
    return provider_name.strip().lower().replace("-", "_")


def _normalize_media_type(
    media_type: str | None,
    media_url: str | None,
    provider_media_id: str | None,
) -> str | None:
    if media_type:
        normalized = media_type.strip().lower().replace("-", "_")
        return "image" if normalized == "photo" else normalized
    if media_url or provider_media_id:
        return "image"
    return None
