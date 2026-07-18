from __future__ import annotations

import mimetypes
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

from app.core.config import settings


@dataclass(frozen=True)
class StoredMediaResult:
    status: str
    storage_url: str | None = None
    storage_provider: str | None = None
    file_name: str | None = None
    mime_type: str | None = None
    byte_size: int | None = None
    error_message: str | None = None
    audit_payload: dict | None = None


def persist_inbound_media(
    normalized_message,
    *,
    company_id: UUID | None,
    project_id: UUID | None = None,
    uploaded_by: UUID | None = None,
) -> StoredMediaResult:
    if not normalized_message.media_type:
        return StoredMediaResult(status="not_media", audit_payload={"status": "not_media"})

    if normalized_message.stored_media_url:
        return StoredMediaResult(
            status=normalized_message.stored_media_status or "already_stored",
            storage_url=normalized_message.stored_media_url,
            audit_payload={"status": normalized_message.stored_media_status or "already_stored"},
        )

    if settings.media_storage_provider != "local_filesystem":
        return StoredMediaResult(
            status="storage_provider_not_supported",
            storage_provider=settings.media_storage_provider,
            error_message=(
                f"Media storage provider {settings.media_storage_provider} is not implemented yet."
            ),
            audit_payload={"status": "storage_provider_not_supported"},
        )

    media_url = normalized_message.media_url
    if not _is_downloadable_url(media_url):
        return StoredMediaResult(
            status="media_url_unavailable",
            storage_provider="local_filesystem",
            error_message="No downloadable media URL was available for persistence.",
            audit_payload={"status": "media_url_unavailable"},
        )

    download_result = _download_media(
        media_url=media_url,
        mime_type=normalized_message.media_mime_type,
        download_headers=normalized_message.media_download_headers,
    )
    if download_result.error_message:
        return StoredMediaResult(
            status="download_failed",
            storage_provider="local_filesystem",
            error_message=download_result.error_message,
            audit_payload={"status": "download_failed"},
        )

    file_name = _safe_file_name(
        normalized_message.media_file_name,
        media_url,
        download_result.mime_type,
        normalized_message.media_type,
    )
    relative_path = _build_relative_storage_path(
        company_id=company_id,
        project_id=project_id,
        media_type=normalized_message.media_type,
        file_name=file_name,
    )
    absolute_path = Path(settings.media_storage_local_root) / relative_path
    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_path.write_bytes(download_result.content or b"")

    storage_url = f"storage://local/{relative_path.as_posix()}"
    return StoredMediaResult(
        status="stored",
        storage_url=storage_url,
        storage_provider="local_filesystem",
        file_name=file_name,
        mime_type=download_result.mime_type,
        byte_size=len(download_result.content or b""),
        audit_payload={
            "status": "stored",
            "storage_provider": "local_filesystem",
            "storage_url": storage_url,
            "file_name": file_name,
            "mime_type": download_result.mime_type,
            "byte_size": len(download_result.content or b""),
        },
    )


@dataclass(frozen=True)
class DownloadedMedia:
    content: bytes | None
    mime_type: str
    error_message: str | None = None


def _download_media(
    *,
    media_url: str,
    mime_type: str | None,
    download_headers: dict[str, str] | None,
) -> DownloadedMedia:
    request_headers = {"User-Agent": "Cognos-AI/0.1", **(download_headers or {})}
    request = urllib.request.Request(media_url, headers=request_headers)
    try:
        with urllib.request.urlopen(
            request,
            timeout=settings.media_storage_download_timeout_seconds,
        ) as response:
            response_mime_type = (response.headers.get_content_type() or "").lower()
            max_bytes = settings.media_storage_max_bytes
            content = response.read(max_bytes + 1)
    except urllib.error.URLError as exc:
        return DownloadedMedia(
            content=None,
            mime_type=mime_type or "application/octet-stream",
            error_message=f"Could not download media: {exc.reason}",
        )

    if len(content) > settings.media_storage_max_bytes:
        return DownloadedMedia(
            content=None,
            mime_type=mime_type or response_mime_type or "application/octet-stream",
            error_message="Media file is larger than the configured storage size limit.",
        )

    return DownloadedMedia(
        content=content,
        mime_type=(mime_type or response_mime_type or "application/octet-stream").split(";")[0],
    )


def _build_relative_storage_path(
    *,
    company_id: UUID | None,
    project_id: UUID | None,
    media_type: str,
    file_name: str,
) -> Path:
    now = datetime.utcnow()
    company_segment = str(company_id) if company_id else "unknown-company"
    project_segment = str(project_id) if project_id else "unassigned-project"
    return Path(
        company_segment,
        project_segment,
        media_type or "media",
        f"{now:%Y}",
        f"{now:%m}",
        f"{uuid4()}-{file_name}",
    )


def _safe_file_name(
    file_name: str | None,
    media_url: str | None,
    mime_type: str | None,
    media_type: str | None,
) -> str:
    candidate = (file_name or urllib.parse.urlparse(media_url or "").path.rsplit("/", 1)[-1]).strip()
    candidate = re.sub(r"[^A-Za-z0-9._-]+", "-", candidate).strip(".-")
    if candidate and "." in candidate:
        return candidate[:140]

    extension = _guess_extension(candidate or media_url)
    if not extension and mime_type:
        extension = (mimetypes.guess_extension(mime_type) or "").lstrip(".")
    if not extension:
        extension = _fallback_extension(media_type)
    stem = candidate[:80] if candidate else "media"
    return f"{stem}.{extension}"


def _guess_extension(value: str | None) -> str | None:
    path = urllib.parse.urlparse(value or "").path
    if "." not in path:
        return None
    return re.sub(r"[^A-Za-z0-9]+", "", path.rsplit(".", 1)[-1].lower()) or None


def _fallback_extension(media_type: str | None) -> str:
    if media_type in {"audio", "voice"}:
        return "ogg"
    if media_type == "image":
        return "jpg"
    if media_type == "video":
        return "mp4"
    return "bin"


def _is_downloadable_url(media_url: str | None) -> bool:
    parsed = urllib.parse.urlparse(media_url or "")
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
