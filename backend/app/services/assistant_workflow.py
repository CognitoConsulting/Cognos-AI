from __future__ import annotations

from dataclasses import dataclass

from app.models import AssistantParseResult


@dataclass(frozen=True)
class ConversationDecision:
    status: str
    pending_intent: str
    pending_data: dict
    missing_fields: list[str]
    confirmation_prompt: str


ACTIONABLE_INTENTS = {
    "progress",
    "manpower",
    "material_received",
    "material_issued",
}


def build_conversation_decision(
    parse_result: AssistantParseResult,
    user_message: str | None,
) -> ConversationDecision:
    """Turn a parsed message into the assistant's next conversational step."""
    if parse_result.intent == "irrelevant_or_offensive":
        return ConversationDecision(
            status="redirected",
            pending_intent=parse_result.intent,
            pending_data=parse_result.extracted_data,
            missing_fields=[],
            confirmation_prompt=(
                parse_result.assistant_summary
                or "Please share a site update related to progress, manpower, materials, or photos."
            ),
        )

    if parse_result.intent not in ACTIONABLE_INTENTS:
        return ConversationDecision(
            status="awaiting_missing_information",
            pending_intent=parse_result.intent,
            pending_data=parse_result.extracted_data,
            missing_fields=parse_result.missing_fields,
            confirmation_prompt=(
                parse_result.assistant_summary
                or "What would you like to record: progress, manpower, material received, or material issued?"
            ),
        )

    if parse_result.missing_fields:
        return ConversationDecision(
            status="awaiting_missing_information",
            pending_intent=parse_result.intent,
            pending_data=parse_result.extracted_data,
            missing_fields=parse_result.missing_fields,
            confirmation_prompt=_build_missing_information_prompt(parse_result),
        )

    return ConversationDecision(
        status="awaiting_confirmation",
        pending_intent=parse_result.intent,
        pending_data=parse_result.extracted_data,
        missing_fields=[],
        confirmation_prompt=_build_confirmation_prompt(parse_result, user_message),
    )


def _build_missing_information_prompt(parse_result: AssistantParseResult) -> str:
    readable_intent = _readable_intent(parse_result.intent)
    readable_missing = ", ".join(_humanize_field(field) for field in parse_result.missing_fields)
    return (
        f"I understood this as a {readable_intent} update, but I still need: "
        f"{readable_missing}. Please send the missing details and I will complete the entry."
    )


def _build_confirmation_prompt(
    parse_result: AssistantParseResult,
    user_message: str | None,
) -> str:
    readable_intent = _readable_intent(parse_result.intent)
    summary = parse_result.assistant_summary or f"{readable_intent.title()} update detected."
    original = f"\n\nOriginal message: {user_message.strip()}" if user_message else ""
    return (
        f"{summary}{original}\n\n"
        "Please reply Yes to save this entry, or tell me what to change."
    )


def _readable_intent(intent: str) -> str:
    labels = {
        "progress": "progress",
        "manpower": "manpower",
        "material_received": "material received",
        "material_issued": "material issued",
    }
    return labels.get(intent, "site")


def _humanize_field(field: str) -> str:
    labels = {
        "activity": "activity or work item",
        "quantity": "quantity",
        "unit": "unit",
        "location": "location or area",
        "trade_counts": "number of workers by trade",
        "material": "material name",
        "intent": "what type of update this is",
    }
    return labels.get(field, field.replace("_", " "))
