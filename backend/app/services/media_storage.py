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


S3_COMPATIBLE_PROVIDERS = {"s3", "s3_compatible", "cloudflare_r2"}


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


@dataclass(frozen=True)
class MediaAccessResult:
    status: str
    access_type: str | None = None
    url: str | None = None
    file_path: Path | None = None
    file_name: str | None = None
    mime_type: str | None = None
    error_message: str | None = None


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

    storage_provider = _normalized_storage_provider()
    if storage_provider not in {"local_filesystem", *S3_COMPATIBLE_PROVIDERS}:
        return StoredMediaResult(
            status="storage_provider_not_supported",
            storage_provider=storage_provider,
            error_message=(
                f"Media storage provider {settings.media_storage_provider} is not implemented yet."
            ),
            audit_payload={"status": "storage_provider_not_supported"},
        )

    media_url = normalized_message.media_url
    if not _is_downloadable_url(media_url):
        return StoredMediaResult(
            status="media_url_unavailable",
            storage_provider=storage_provider,
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
            storage_provider=storage_provider,
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

    if storage_provider in S3_COMPATIBLE_PROVIDERS:
        return _store_s3_compatible_media(
            content=download_result.content or b"",
            relative_path=relative_path,
            file_name=file_name,
            mime_type=download_result.mime_type,
            byte_size=len(download_result.content or b""),
            storage_provider=storage_provider,
        )

    return _store_local_media(
        content=download_result.content or b"",
        relative_path=relative_path,
        file_name=file_name,
        mime_type=download_result.mime_type,
        byte_size=len(download_result.content or b""),
    )


def resolve_media_access(
    storage_url: str,
    *,
    file_name: str | None = None,
    mime_type: str | None = None,
) -> MediaAccessResult:
    parsed = urllib.parse.urlparse(storage_url or "")
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return MediaAccessResult(
            status="accessible",
            access_type="redirect",
            url=storage_url,
            file_name=file_name,
            mime_type=mime_type,
        )

    if parsed.scheme != "storage" or not parsed.netloc:
        return MediaAccessResult(
            status="invalid_storage_url",
            error_message="The stored media reference is not a supported storage URL.",
        )

    storage_provider = parsed.netloc.strip().lower().replace("-", "_")
    if storage_provider == "local":
        return _resolve_local_media_access(parsed, file_name=file_name, mime_type=mime_type)

    if storage_provider in S3_COMPATIBLE_PROVIDERS:
        return _resolve_s3_compatible_media_access(
            parsed,
            storage_provider=storage_provider,
            file_name=file_name,
            mime_type=mime_type,
        )

    return MediaAccessResult(
        status="unsupported_storage_provider",
        error_message=f"Media storage provider {storage_provider} is not supported for access.",
    )


def _store_local_media(
    *,
    content: bytes,
    relative_path: Path,
    file_name: str,
    mime_type: str,
    byte_size: int,
) -> StoredMediaResult:
    absolute_path = Path(settings.media_storage_local_root) / relative_path
    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_path.write_bytes(content)

    storage_url = f"storage://local/{relative_path.as_posix()}"
    return StoredMediaResult(
        status="stored",
        storage_url=storage_url,
        storage_provider="local_filesystem",
        file_name=file_name,
        mime_type=mime_type,
        byte_size=byte_size,
        audit_payload={
            "status": "stored",
            "storage_provider": "local_filesystem",
            "storage_url": storage_url,
            "file_name": file_name,
            "mime_type": mime_type,
            "byte_size": byte_size,
        },
    )


def _resolve_local_media_access(
    parsed: urllib.parse.ParseResult,
    *,
    file_name: str | None,
    mime_type: str | None,
) -> MediaAccessResult:
    relative_url_path = urllib.parse.unquote(parsed.path.lstrip("/"))
    if not relative_url_path:
        return MediaAccessResult(
            status="invalid_storage_url",
            error_message="The local media reference does not include a file path.",
        )

    storage_root = Path(settings.media_storage_local_root).resolve()
    file_path = (storage_root / Path(relative_url_path)).resolve()
    try:
        file_path.relative_to(storage_root)
    except ValueError:
        return MediaAccessResult(
            status="invalid_storage_url",
            error_message="The local media reference points outside the configured storage folder.",
        )

    if not file_path.is_file():
        return MediaAccessResult(
            status="not_found",
            error_message="The stored media file could not be found.",
        )

    guessed_mime_type = mime_type or mimetypes.guess_type(file_path.name)[0]
    return MediaAccessResult(
        status="accessible",
        access_type="file",
        file_path=file_path,
        file_name=file_name or file_path.name,
        mime_type=guessed_mime_type or "application/octet-stream",
    )


def _store_s3_compatible_media(
    *,
    content: bytes,
    relative_path: Path,
    file_name: str,
    mime_type: str,
    byte_size: int,
    storage_provider: str,
) -> StoredMediaResult:
    bucket = (settings.media_storage_s3_bucket or "").strip()
    if not bucket:
        return StoredMediaResult(
            status="storage_bucket_not_configured",
            storage_provider=storage_provider,
            error_message="S3-compatible media storage requires MEDIA_STORAGE_S3_BUCKET.",
            audit_payload={"status": "storage_bucket_not_configured"},
        )

    access_key = _secret_value(settings.media_storage_s3_access_key_id)
    secret_key = _secret_value(settings.media_storage_s3_secret_access_key)
    if not access_key or not secret_key:
        return StoredMediaResult(
            status="storage_credentials_not_configured",
            storage_provider=storage_provider,
            error_message=(
                "S3-compatible media storage requires MEDIA_STORAGE_S3_ACCESS_KEY_ID "
                "and MEDIA_STORAGE_S3_SECRET_ACCESS_KEY."
            ),
            audit_payload={"status": "storage_credentials_not_configured"},
        )

    object_key = _s3_object_key(relative_path)
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError

        client = boto3.client(
            "s3",
            region_name=settings.media_storage_s3_region or None,
            endpoint_url=settings.media_storage_s3_endpoint_url or None,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        client.put_object(
            Bucket=bucket,
            Key=object_key,
            Body=content,
            ContentType=mime_type,
        )
    except ImportError as exc:
        return StoredMediaResult(
            status="storage_dependency_missing",
            storage_provider=storage_provider,
            error_message="boto3 is required for S3-compatible media storage.",
            audit_payload={"status": "storage_dependency_missing"},
        )
    except (BotoCoreError, ClientError) as exc:
        return StoredMediaResult(
            status="upload_failed",
            storage_provider=storage_provider,
            error_message=f"S3-compatible upload failed: {exc}",
            audit_payload={"status": "upload_failed", "bucket": bucket, "object_key": object_key},
        )

    storage_url = _s3_storage_url(
        bucket=bucket,
        object_key=object_key,
        storage_provider=storage_provider,
    )
    return StoredMediaResult(
        status="stored",
        storage_url=storage_url,
        storage_provider=storage_provider,
        file_name=file_name,
        mime_type=mime_type,
        byte_size=byte_size,
        audit_payload={
            "status": "stored",
            "storage_provider": storage_provider,
            "storage_url": storage_url,
            "bucket": bucket,
            "object_key": object_key,
            "file_name": file_name,
            "mime_type": mime_type,
            "byte_size": byte_size,
        },
    )


def _resolve_s3_compatible_media_access(
    parsed: urllib.parse.ParseResult,
    *,
    storage_provider: str,
    file_name: str | None,
    mime_type: str | None,
) -> MediaAccessResult:
    bucket = parsed.path.lstrip("/").split("/", 1)[0]
    object_key = parsed.path.lstrip("/").split("/", 1)[1] if "/" in parsed.path.lstrip("/") else ""
    if not bucket or not object_key:
        return MediaAccessResult(
            status="invalid_storage_url",
            error_message="The S3-compatible media reference is missing a bucket or object key.",
        )

    public_base_url = (settings.media_storage_s3_public_base_url or "").strip().rstrip("/")
    if public_base_url:
        return MediaAccessResult(
            status="accessible",
            access_type="redirect",
            url=f"{public_base_url}/{urllib.parse.quote(object_key, safe='/')}",
            file_name=file_name,
            mime_type=mime_type,
        )

    access_key = _secret_value(settings.media_storage_s3_access_key_id)
    secret_key = _secret_value(settings.media_storage_s3_secret_access_key)
    if not access_key or not secret_key:
        return MediaAccessResult(
            status="storage_credentials_not_configured",
            error_message=(
                "S3-compatible media access requires MEDIA_STORAGE_S3_ACCESS_KEY_ID "
                "and MEDIA_STORAGE_S3_SECRET_ACCESS_KEY."
            ),
        )

    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError

        client = boto3.client(
            "s3",
            region_name=settings.media_storage_s3_region or None,
            endpoint_url=settings.media_storage_s3_endpoint_url or None,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": object_key},
            ExpiresIn=settings.media_storage_s3_presigned_url_ttl_seconds,
        )
    except ImportError:
        return MediaAccessResult(
            status="storage_dependency_missing",
            error_message="boto3 is required for S3-compatible media access.",
        )
    except (BotoCoreError, ClientError) as exc:
        return MediaAccessResult(
            status="presign_failed",
            error_message=f"S3-compatible media access failed: {exc}",
        )

    return MediaAccessResult(
        status="accessible",
        access_type="redirect",
        url=url,
        file_name=file_name,
        mime_type=mime_type,
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


def _normalized_storage_provider() -> str:
    return settings.media_storage_provider.strip().lower().replace("-", "_")


def _secret_value(secret) -> str | None:
    if not secret:
        return None
    value = secret.get_secret_value() if hasattr(secret, "get_secret_value") else str(secret)
    return value.strip() or None


def _s3_object_key(relative_path: Path) -> str:
    prefix = settings.media_storage_s3_prefix.strip().strip("/")
    path = relative_path.as_posix()
    return f"{prefix}/{path}" if prefix else path


def _s3_storage_url(*, bucket: str, object_key: str, storage_provider: str) -> str:
    public_base_url = (settings.media_storage_s3_public_base_url or "").strip().rstrip("/")
    if public_base_url:
        return f"{public_base_url}/{urllib.parse.quote(object_key, safe='/')}"
    return f"storage://{storage_provider}/{bucket}/{object_key}"
