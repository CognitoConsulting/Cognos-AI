from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class NormalizedInboundMessage:
    provider_name: str
    provider_message_id: str | None
    provider_account_id: str | None
    phone: str | None
    message_text: str | None
    raw_payload: dict[str, Any]


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

    if not any([message_text, phone, provider_message_id]):
        return None

    return NormalizedInboundMessage(
        provider_name=provider_name,
        provider_message_id=provider_message_id,
        provider_account_id=provider_account_id,
        phone=phone,
        message_text=message_text,
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
    if message_type == "text":
        text_body = (message.get("text") or {}).get("body")
    elif message_type in {"button", "interactive"}:
        text_body = _extract_interactive_text(message)

    return NormalizedInboundMessage(
        provider_name=provider_name,
        provider_message_id=_first_text(message.get("id")),
        provider_account_id=provider_account_id,
        phone=_first_text(message.get("from")),
        message_text=_first_text(text_body),
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
