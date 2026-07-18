from __future__ import annotations

import json
import mimetypes
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from uuid import UUID

from app.core.config import settings
from app.models import Company


VOICE_MEDIA_TYPES = {"audio", "voice"}
OPENAI_PROVIDER_NAMES = {"openai", "platform_openai"}
SUPPORTED_OPENAI_EXTENSIONS = {
    "flac",
    "m4a",
    "mp3",
    "mp4",
    "mpeg",
    "mpga",
    "ogg",
    "wav",
    "webm",
}
SUPPORTED_OPENAI_MIME_TYPES = {
    "audio/flac",
    "audio/x-flac",
    "audio/m4a",
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/mpga",
    "audio/ogg",
    "audio/wav",
    "audio/x-wav",
    "audio/webm",
    "video/mp4",
    "video/webm",
}


@dataclass(frozen=True)
class VoiceTranscriptionResult:
    status: str
    transcript_text: str | None
    provider_name: str
    language: str | None = None
    error_message: str | None = None


def is_voice_media_type(media_type: str | None) -> bool:
    return (media_type or "").strip().lower() in VOICE_MEDIA_TYPES


def transcribe_voice_note(normalized_message, company: Company | None = None) -> VoiceTranscriptionResult:
    """Return a transcript when possible, otherwise a precise operational status.

    Provider-supplied transcripts are trusted first because some WhatsApp gateways
    may perform transcription before forwarding the webhook. When OpenAI
    transcription is enabled, this adapter downloads supported audio files and
    submits them to the Audio Transcriptions API.
    """
    if normalized_message.transcription_text:
        return VoiceTranscriptionResult(
            status="transcribed",
            transcript_text=normalized_message.transcription_text,
            provider_name="provider_supplied",
            language=None,
        )

    if not settings.voice_transcription_enabled:
        return VoiceTranscriptionResult(
            status="not_configured",
            transcript_text=None,
            provider_name=settings.voice_transcription_provider,
            error_message="Voice transcription is not configured for this environment.",
        )

    if settings.voice_transcription_provider not in OPENAI_PROVIDER_NAMES:
        return VoiceTranscriptionResult(
            status="queued",
            transcript_text=None,
            provider_name=settings.voice_transcription_provider,
            error_message=(
                "Voice transcription is enabled, but the selected transcription provider "
                "is not implemented yet."
            ),
        )

    api_key_result = _resolve_openai_api_key(company)
    if not api_key_result.api_key:
        return VoiceTranscriptionResult(
            status=api_key_result.status,
            transcript_text=None,
            provider_name=api_key_result.provider_name,
            error_message=api_key_result.error_message,
        )

    media_url = normalized_message.media_url
    if not _is_downloadable_url(media_url):
        return VoiceTranscriptionResult(
            status="media_unavailable",
            transcript_text=None,
            provider_name=api_key_result.provider_name,
            error_message=(
                "The voice note does not include a downloadable media URL yet. "
                "Provider media-ID download is still future work."
            ),
        )

    if not _is_supported_openai_audio(
        media_url=media_url,
        file_name=normalized_message.media_file_name,
        mime_type=normalized_message.media_mime_type,
    ):
        return VoiceTranscriptionResult(
            status="unsupported_format",
            transcript_text=None,
            provider_name=api_key_result.provider_name,
            error_message=(
                "The voice note format is not supported by the current OpenAI file "
                "transcription adapter. Convert it to flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, "
                "or webm before transcription."
            ),
        )

    audio_result = _download_audio_file(
        media_url=media_url,
        file_name=normalized_message.media_file_name,
        mime_type=normalized_message.media_mime_type,
    )
    if audio_result.error_message:
        return VoiceTranscriptionResult(
            status="download_failed",
            transcript_text=None,
            provider_name=api_key_result.provider_name,
            error_message=audio_result.error_message,
        )

    try:
        transcript_text = _create_openai_transcription(
            api_key=api_key_result.api_key,
            audio=audio_result,
        )
    except Exception as exc:
        return VoiceTranscriptionResult(
            status="transcription_failed",
            transcript_text=None,
            provider_name=api_key_result.provider_name,
            error_message=f"OpenAI transcription failed: {exc}",
        )

    return VoiceTranscriptionResult(
        status="transcribed",
        transcript_text=transcript_text,
        provider_name=api_key_result.provider_name,
        language=None,
    )


@dataclass(frozen=True)
class OpenAIKeyResolution:
    api_key: str | None
    provider_name: str
    status: str
    error_message: str | None = None


@dataclass(frozen=True)
class DownloadedAudio:
    content: bytes | None
    file_name: str
    mime_type: str
    error_message: str | None = None


def _resolve_openai_api_key(company: Company | None) -> OpenAIKeyResolution:
    if company and company.ai_key_mode == "company_owned":
        company_key = _company_owned_openai_key(company.id)
        if company_key:
            return OpenAIKeyResolution(
                api_key=company_key,
                provider_name="openai_company_owned",
                status="configured",
            )
        return OpenAIKeyResolution(
            api_key=None,
            provider_name="openai_company_owned",
            status="company_key_not_configured",
            error_message=(
                "This company is configured for company-owned AI keys, but no company-owned "
                "OpenAI key is available in the runtime secret environment."
            ),
        )

    if settings.openai_api_key:
        return OpenAIKeyResolution(
            api_key=settings.openai_api_key.get_secret_value(),
            provider_name="openai_platform_managed",
            status="configured",
        )

    return OpenAIKeyResolution(
        api_key=None,
        provider_name="openai_platform_managed",
        status="platform_key_not_configured",
        error_message=(
            "Platform-managed OpenAI transcription is enabled, but OPENAI_API_KEY is not configured."
        ),
    )


def _company_owned_openai_key(company_id: UUID) -> str | None:
    normalized_company_id = str(company_id).replace("-", "_").upper()
    return os.getenv(f"COGNOS_COMPANY_OPENAI_API_KEY_{normalized_company_id}")


def _is_downloadable_url(media_url: str | None) -> bool:
    parsed = urllib.parse.urlparse(media_url or "")
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _is_supported_openai_audio(
    *,
    media_url: str | None,
    file_name: str | None,
    mime_type: str | None,
) -> bool:
    normalized_mime = (mime_type or "").split(";")[0].strip().lower()
    if normalized_mime in SUPPORTED_OPENAI_MIME_TYPES:
        return True

    guessed_mime, _ = mimetypes.guess_type(file_name or media_url or "")
    if guessed_mime and guessed_mime.lower() in SUPPORTED_OPENAI_MIME_TYPES:
        return True

    extension = _guess_extension(file_name or media_url)
    return extension in SUPPORTED_OPENAI_EXTENSIONS


def _download_audio_file(
    *,
    media_url: str,
    file_name: str | None,
    mime_type: str | None,
) -> DownloadedAudio:
    request = urllib.request.Request(media_url, headers={"User-Agent": "Cognos-AI/0.1"})
    try:
        with urllib.request.urlopen(
            request,
            timeout=settings.voice_transcription_download_timeout_seconds,
        ) as response:
            response_mime_type = (response.headers.get_content_type() or "").lower()
            max_bytes = settings.voice_transcription_max_bytes
            content = response.read(max_bytes + 1)
    except urllib.error.URLError as exc:
        return DownloadedAudio(
            content=None,
            file_name=_safe_audio_file_name(file_name, media_url),
            mime_type=mime_type or "application/octet-stream",
            error_message=f"Could not download voice media: {exc.reason}",
        )

    if len(content) > settings.voice_transcription_max_bytes:
        return DownloadedAudio(
            content=None,
            file_name=_safe_audio_file_name(file_name, media_url),
            mime_type=mime_type or response_mime_type or "application/octet-stream",
            error_message="Voice media is larger than the configured transcription size limit.",
        )

    resolved_mime_type = (mime_type or response_mime_type or "application/octet-stream").split(";")[0]
    return DownloadedAudio(
        content=content,
        file_name=_safe_audio_file_name(file_name, media_url, resolved_mime_type),
        mime_type=resolved_mime_type,
    )


def _create_openai_transcription(*, api_key: str, audio: DownloadedAudio) -> str:
    boundary = "cognos_ai_transcription_boundary"
    body = _multipart_form_data(
        boundary=boundary,
        fields={"model": settings.openai_transcription_model, "response_format": "json"},
        file_field="file",
        file_name=audio.file_name,
        file_content=audio.content or b"",
        file_mime_type=audio.mime_type,
    )
    request = urllib.request.Request(
        "https://api.openai.com/v1/audio/transcriptions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{exc.code} {error_body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(str(exc.reason)) from exc

    transcript_text = str(payload.get("text") or "").strip()
    if not transcript_text:
        raise RuntimeError("OpenAI returned an empty transcription response.")
    return transcript_text


def _multipart_form_data(
    *,
    boundary: str,
    fields: dict[str, str],
    file_field: str,
    file_name: str,
    file_content: bytes,
    file_mime_type: str,
) -> bytes:
    lines: list[bytes] = []
    for name, value in fields.items():
        lines.extend(
            [
                f"--{boundary}".encode(),
                f'Content-Disposition: form-data; name="{name}"'.encode(),
                b"",
                value.encode(),
            ]
        )
    lines.extend(
        [
            f"--{boundary}".encode(),
            (
                f'Content-Disposition: form-data; name="{file_field}"; '
                f'filename="{file_name}"'
            ).encode(),
            f"Content-Type: {file_mime_type}".encode(),
            b"",
            file_content,
            f"--{boundary}--".encode(),
            b"",
        ]
    )
    return b"\r\n".join(lines)


def _safe_audio_file_name(
    file_name: str | None,
    media_url: str | None,
    mime_type: str | None = None,
) -> str:
    candidate = (file_name or urllib.parse.urlparse(media_url or "").path.rsplit("/", 1)[-1]).strip()
    if candidate and "." in candidate:
        return candidate[:120]

    extension = _guess_extension(candidate or media_url)
    if not extension and mime_type:
        extension = (mimetypes.guess_extension(mime_type) or "").lstrip(".")
    return f"voice-note.{extension or 'mp3'}"


def _guess_extension(value: str | None) -> str | None:
    path = urllib.parse.urlparse(value or "").path
    if "." not in path:
        return None
    return path.rsplit(".", 1)[-1].lower()
