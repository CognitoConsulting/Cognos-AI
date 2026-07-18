from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from app.core.config import settings
from app.models import WhatsAppProviderAccount


META_PROVIDER_NAMES = {"meta", "meta_cloud_api", "whatsapp_cloud_api"}


@dataclass(frozen=True)
class ProviderMediaResolution:
    status: str
    media_url: str | None = None
    mime_type: str | None = None
    file_size: int | None = None
    sha256: str | None = None
    download_headers: dict[str, str] | None = None
    provider_name: str | None = None
    error_message: str | None = None
    audit_payload: dict | None = None


def resolve_provider_media_url(
    normalized_message,
    provider_account: WhatsAppProviderAccount | None,
) -> ProviderMediaResolution:
    """Resolve a provider media ID into a short-lived downloadable media URL.

    The rest of the application stays provider-neutral. This function contains the
    Meta-specific two-step media lookup: media ID -> URL, then later URL -> bytes.
    """
    if normalized_message.media_url:
        return ProviderMediaResolution(
            status="already_available",
            media_url=normalized_message.media_url,
            mime_type=normalized_message.media_mime_type,
            download_headers=normalized_message.media_download_headers,
            provider_name=normalized_message.provider_name,
            audit_payload={"status": "already_available"},
        )

    if not normalized_message.provider_media_id:
        return ProviderMediaResolution(
            status="no_provider_media_id",
            provider_name=normalized_message.provider_name,
            error_message="No provider media ID was supplied in the webhook payload.",
            audit_payload={"status": "no_provider_media_id"},
        )

    if normalized_message.provider_name not in META_PROVIDER_NAMES:
        return ProviderMediaResolution(
            status="provider_not_supported",
            provider_name=normalized_message.provider_name,
            error_message=(
                f"Media URL lookup is not implemented for provider "
                f"{normalized_message.provider_name}."
            ),
            audit_payload={"status": "provider_not_supported"},
        )

    token_result = _resolve_meta_access_token(provider_account)
    if not token_result.access_token:
        return ProviderMediaResolution(
            status=token_result.status,
            provider_name=normalized_message.provider_name,
            error_message=token_result.error_message,
            audit_payload={
                "status": token_result.status,
                "provider_account_id": provider_account.provider_account_id if provider_account else None,
                "phone_number_id": provider_account.phone_number_id if provider_account else None,
            },
        )

    return _retrieve_meta_media_url(
        media_id=normalized_message.provider_media_id,
        access_token=token_result.access_token,
        provider_name=normalized_message.provider_name,
    )


@dataclass(frozen=True)
class MetaAccessTokenResolution:
    access_token: str | None
    status: str
    error_message: str | None = None


def _resolve_meta_access_token(
    provider_account: WhatsAppProviderAccount | None,
) -> MetaAccessTokenResolution:
    if provider_account:
        account_key = _meta_account_token_env_name(provider_account)
        account_token = os.getenv(account_key)
        if account_token:
            return MetaAccessTokenResolution(access_token=account_token, status="configured")

    if settings.meta_whatsapp_access_token:
        return MetaAccessTokenResolution(
            access_token=settings.meta_whatsapp_access_token.get_secret_value(),
            status="configured",
        )

    expected_key = _meta_account_token_env_name(provider_account) if provider_account else None
    return MetaAccessTokenResolution(
        access_token=None,
        status="meta_access_token_not_configured",
        error_message=(
            "Meta WhatsApp media download needs a runtime access token. Set "
            f"{expected_key} or META_WHATSAPP_ACCESS_TOKEN."
            if expected_key
            else "Meta WhatsApp media download needs META_WHATSAPP_ACCESS_TOKEN."
        ),
    )


def _retrieve_meta_media_url(
    *,
    media_id: str,
    access_token: str,
    provider_name: str,
) -> ProviderMediaResolution:
    graph_version = settings.meta_graph_api_version.strip().strip("/")
    request_url = f"https://graph.facebook.com/{graph_version}/{urllib.parse.quote(media_id)}"
    request = urllib.request.Request(
        request_url,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    try:
        with urllib.request.urlopen(
            request,
            timeout=settings.whatsapp_media_download_timeout_seconds,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        return ProviderMediaResolution(
            status="meta_media_lookup_failed",
            provider_name=provider_name,
            error_message=f"Meta media lookup failed: {exc.code} {error_body}",
            audit_payload={"status": "meta_media_lookup_failed", "http_status": exc.code},
        )
    except urllib.error.URLError as exc:
        return ProviderMediaResolution(
            status="meta_media_lookup_failed",
            provider_name=provider_name,
            error_message=f"Meta media lookup failed: {exc.reason}",
            audit_payload={"status": "meta_media_lookup_failed"},
        )

    media_url = str(payload.get("url") or "").strip()
    if not media_url:
        return ProviderMediaResolution(
            status="meta_media_url_missing",
            provider_name=provider_name,
            error_message="Meta media lookup succeeded but did not return a media URL.",
            audit_payload={"status": "meta_media_url_missing"},
        )

    return ProviderMediaResolution(
        status="resolved",
        media_url=media_url,
        mime_type=str(payload.get("mime_type") or "").strip() or None,
        file_size=_int_or_none(payload.get("file_size")),
        sha256=str(payload.get("sha256") or "").strip() or None,
        download_headers={"Authorization": f"Bearer {access_token}"},
        provider_name=provider_name,
        audit_payload={
            "status": "resolved",
            "mime_type": payload.get("mime_type"),
            "file_size": payload.get("file_size"),
            "sha256": payload.get("sha256"),
        },
    )


def _meta_account_token_env_name(provider_account: WhatsAppProviderAccount | None) -> str:
    if not provider_account:
        return "META_WHATSAPP_ACCESS_TOKEN"

    token_scope = provider_account.phone_number_id or provider_account.provider_account_id
    if not token_scope:
        return "META_WHATSAPP_ACCESS_TOKEN"

    normalized_scope = "".join(
        character if character.isalnum() else "_"
        for character in token_scope.strip().upper()
    )
    return f"META_WHATSAPP_ACCESS_TOKEN_{normalized_scope}"


def _int_or_none(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
