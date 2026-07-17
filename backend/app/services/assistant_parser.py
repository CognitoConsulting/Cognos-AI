from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ParsedAssistantMessage:
    intent: str
    confidence: str
    input_language: str | None
    extracted_data: dict = field(default_factory=dict)
    missing_fields: list[str] = field(default_factory=list)
    validation_status: str = "needs_confirmation"
    assistant_summary: str | None = None
    next_action: str = "ask_confirmation"


OFFENSIVE_TERMS = {
    "fuck",
    "shit",
    "bitch",
    "madarchod",
    "bhosdike",
    "bsdk",
}

PROGRESS_TERMS = {
    "completed",
    "complete",
    "done",
    "hua",
    "kiya",
    "finish",
    "finished",
}

MANPOWER_TERMS = {
    "mason",
    "helper",
    "labour",
    "labor",
    "mazdoor",
    "electrician",
    "plumber",
    "carpenter",
    "painter",
}

MATERIAL_RECEIVED_TERMS = {
    "received",
    "receive",
    "aaya",
    "aaye",
    "site par receive",
}

MATERIAL_ISSUED_TERMS = {
    "issued",
    "issue",
    "diya",
    "liye",
    "nikala",
}

MATERIAL_TERMS = {
    "cement",
    "steel",
    "brick",
    "bricks",
    "sand",
    "aggregate",
    "tiles",
    "paint",
}

UNIT_TERMS = {
    "sqm",
    "sqft",
    "cum",
    "bags",
    "bag",
    "kg",
    "ton",
    "tons",
    "nos",
    "pieces",
}


def parse_message(message_text: str | None) -> ParsedAssistantMessage:
    text = (message_text or "").strip()
    lowered = text.lower()

    if not text:
        return ParsedAssistantMessage(
            intent="unknown",
            confidence="low",
            input_language=None,
            missing_fields=["message_text"],
            validation_status="missing_information",
            assistant_summary="I could not find any message content to process.",
            next_action="ask_missing_information",
        )

    language = _detect_language(lowered)

    if _contains_any(lowered, OFFENSIVE_TERMS):
        return ParsedAssistantMessage(
            intent="irrelevant_or_offensive",
            confidence="high",
            input_language=language,
            extracted_data={"original_text": text},
            validation_status="rejected",
            assistant_summary=(
                "I can help with project updates such as progress, manpower, "
                "materials, and site images. Please share the site update you want to record."
            ),
            next_action="redirect_professionally",
        )

    if _looks_like_material_received(lowered):
        return _parse_material(text, lowered, language, "material_received")

    if _looks_like_material_issued(lowered):
        return _parse_material(text, lowered, language, "material_issued")

    if _contains_any(lowered, MANPOWER_TERMS):
        return _parse_manpower(text, lowered, language)

    if _looks_like_progress(lowered):
        return _parse_progress(text, lowered, language)

    return ParsedAssistantMessage(
        intent="unknown",
        confidence="low",
        input_language=language,
        extracted_data={"original_text": text},
        missing_fields=["intent"],
        validation_status="missing_information",
        assistant_summary=(
            "I can help record progress, manpower, material received, material issued, "
            "or site images. What would you like to update?"
        ),
        next_action="ask_missing_information",
    )


def _parse_progress(text: str, lowered: str, language: str) -> ParsedAssistantMessage:
    quantity, unit = _extract_quantity_and_unit(lowered)
    location = _extract_location(text)
    activity = _extract_activity(text)
    missing = []
    if not activity:
        missing.append("activity")
    if quantity is None:
        missing.append("quantity")
    if not unit:
        missing.append("unit")
    if not location:
        missing.append("location")

    extracted = {
        "activity": activity,
        "quantity": quantity,
        "unit": unit,
        "location": location,
        "original_text": text,
    }
    return ParsedAssistantMessage(
        intent="progress",
        confidence="medium" if missing else "high",
        input_language=language,
        extracted_data=extracted,
        missing_fields=missing,
        validation_status="missing_information" if missing else "needs_confirmation",
        assistant_summary=_build_summary("Progress", extracted, missing),
        next_action="ask_missing_information" if missing else "ask_confirmation",
    )


def _parse_manpower(text: str, lowered: str, language: str) -> ParsedAssistantMessage:
    trades = _extract_trades(lowered)
    location = _extract_location(text)
    missing = []
    if not trades:
        missing.append("trade_counts")
    if not location:
        missing.append("location")
    extracted = {
        "trade_counts": trades,
        "location": location,
        "original_text": text,
    }
    return ParsedAssistantMessage(
        intent="manpower",
        confidence="medium" if missing else "high",
        input_language=language,
        extracted_data=extracted,
        missing_fields=missing,
        validation_status="missing_information" if missing else "needs_confirmation",
        assistant_summary=_build_summary("Manpower", extracted, missing),
        next_action="ask_missing_information" if missing else "ask_confirmation",
    )


def _parse_material(
    text: str,
    lowered: str,
    language: str,
    intent: str,
) -> ParsedAssistantMessage:
    quantity, unit = _extract_quantity_and_unit(lowered)
    material = _extract_material(lowered)
    location = _extract_location(text)
    missing = []
    if not material:
        missing.append("material")
    if quantity is None:
        missing.append("quantity")
    if not unit:
        missing.append("unit")
    extracted = {
        "material": material,
        "quantity": quantity,
        "unit": unit,
        "location": location,
        "original_text": text,
    }
    title = "Material received" if intent == "material_received" else "Material issued"
    return ParsedAssistantMessage(
        intent=intent,
        confidence="medium" if missing else "high",
        input_language=language,
        extracted_data=extracted,
        missing_fields=missing,
        validation_status="missing_information" if missing else "needs_confirmation",
        assistant_summary=_build_summary(title, extracted, missing),
        next_action="ask_missing_information" if missing else "ask_confirmation",
    )


def _looks_like_progress(lowered: str) -> bool:
    return _contains_any(lowered, PROGRESS_TERMS)


def _looks_like_material_received(lowered: str) -> bool:
    return _contains_any(lowered, MATERIAL_RECEIVED_TERMS) and _contains_any(
        lowered, MATERIAL_TERMS
    )


def _looks_like_material_issued(lowered: str) -> bool:
    return _contains_any(lowered, MATERIAL_ISSUED_TERMS) and _contains_any(
        lowered, MATERIAL_TERMS
    )


def _contains_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


def _detect_language(lowered: str) -> str:
    hinglish_terms = {"aaj", "hua", "kaam", "mazdoor", "aaye", "diya", "liye"}
    if _contains_any(lowered, hinglish_terms):
        return "hinglish"
    return "english"


def _extract_quantity_and_unit(lowered: str) -> tuple[float | None, str | None]:
    unit_pattern = "|".join(sorted(UNIT_TERMS, key=len, reverse=True))
    pattern = rf"(\d+(?:\.\d+)?)\s*({unit_pattern})\b"
    match = re.search(pattern, lowered)
    if match:
        return float(match.group(1)), match.group(2)

    separated_unit_pattern = rf"(\d+(?:\.\d+)?)(?:\s+[a-z]+){{1,3}}\s+({unit_pattern})\b"
    separated_match = re.search(separated_unit_pattern, lowered)
    if separated_match:
        return float(separated_match.group(1)), separated_match.group(2)

    number = re.search(r"\b(\d+(?:\.\d+)?)\b", lowered)
    return (float(number.group(1)), None) if number else (None, None)


def _extract_location(text: str) -> str | None:
    patterns = [
        r"((?:Tower|Block)\s+[A-Z0-9]+(?:\s+Floor\s+\d+)?)",
        r"(Floor\s+\d+)",
        r"(Basement(?:\s+\d+)?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _extract_activity(text: str) -> str | None:
    lowered = text.lower()
    known_activities = ["plastering", "plaster", "brickwork", "waterproofing", "painting", "tiling", "excavation", "concreting"]
    for activity in known_activities:
        if activity in lowered:
            return "plastering" if activity == "plaster" else activity
    return None


def _extract_material(lowered: str) -> str | None:
    for material in MATERIAL_TERMS:
        if material in lowered:
            return material
    return None


def _extract_trades(lowered: str) -> dict[str, int]:
    trades: dict[str, int] = {}
    for trade in MANPOWER_TERMS:
        match = re.search(rf"\b(\d+)\s+{re.escape(trade)}s?\b", lowered)
        if match:
            trades[trade] = int(match.group(1))
    return trades


def _build_summary(title: str, extracted: dict, missing: list[str]) -> str:
    if missing:
        return f"{title} update detected, but missing: {', '.join(missing)}."
    details = []
    for key, value in extracted.items():
        if key == "original_text" or value in [None, {}, []]:
            continue
        details.append(f"{key}: {value}")
    return f"{title} update detected. " + "; ".join(details)
