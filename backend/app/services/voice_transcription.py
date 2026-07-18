from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


VOICE_MEDIA_TYPES = {"audio", "voice"}


@dataclass(frozen=True)
class VoiceTranscriptionResult:
    status: str
    transcript_text: str | None
    provider_name: str
    language: str | None = None
    error_message: str | None = None


def is_voice_media_type(media_type: str | None) -> bool:
    return (media_type or "").strip().lower() in VOICE_MEDIA_TYPES


def transcribe_voice_note(normalized_message) -> VoiceTranscriptionResult:
    """Return a transcript when one is already available, otherwise record readiness.

    The MVP has not selected a final AI/transcription provider yet. This function
    keeps that decision isolated: webhook code can capture voice notes today, and a
    future provider implementation can be added here without changing the assistant
    workflow.
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

    return VoiceTranscriptionResult(
        status="queued",
        transcript_text=None,
        provider_name=settings.voice_transcription_provider,
        error_message=(
            "Voice transcription is enabled, but the provider implementation is not connected yet."
        ),
    )
