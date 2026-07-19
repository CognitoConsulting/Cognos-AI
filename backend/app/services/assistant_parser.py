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
    "cast",
    "casting",
    "finish",
    "finished",
}

MANPOWER_TERMS = {
    "mason",
    "helper",
    "labour",
    "labor",
    "mazdoor",
    "mistri",
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
    "tmt",
    "rebar",
    "saria",
    "brick",
    "bricks",
    "sand",
    "aggregate",
    "tiles",
    "paint",
}

ACTIVITY_ALIASES = {
    "bar bending": {"bar bending", "barbending"},
    "blockwork": {"blockwork", "block work", "block masonry"},
    "brickwork": {"brickwork", "brick work", "brick masonry"},
    "concreting": {"concreting", "concrete", "rcc", "rcc work"},
    "excavation": {"excavation", "excavating"},
    "painting": {"painting", "paint work"},
    "plastering": {"plastering", "plaster"},
    "shuttering": {"shuttering", "formwork", "form work"},
    "slab casting": {"slab casting", "slab cast", "slab concreting", "slab"},
    "steel fixing": {"steel fixing", "rebar fixing", "tmt fixing"},
    "tiling": {"tiling", "tile work"},
    "waterproofing": {"waterproofing", "water proofing"},
}

MATERIAL_ALIASES = {
    "aggregate": {"aggregate", "aggregates"},
    "brick": {"brick", "bricks"},
    "cement": {"cement"},
    "paint": {"paint"},
    "sand": {"sand"},
    "steel": {"steel", "tmt", "rebar", "saria", "steel bar", "steel bars", "rod", "rods"},
    "tiles": {"tiles", "tile"},
}

TRADE_ALIASES = {
    "carpenter": {"carpenter"},
    "electrician": {"electrician"},
    "helper": {"helper", "helpers", "belder", "beldar"},
    "labour": {"labour", "labor", "mazdoor", "labours", "labors"},
    "mason": {"mason", "masons", "mistri", "mistris"},
    "painter": {"painter"},
    "plumber": {"plumber"},
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
            assistant_summary=(
                "I did not receive any message text. Please send the site update again."
            ),
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
                "I can help record site progress, manpower, material movement, and proofs. "
                "Please send the project update in simple work-related language."
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
            "I can record progress, manpower, material received, material issued, or site "
            "proofs. Please tell me what you want to update."
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
    return any(re.search(rf"\b{re.escape(term)}\b", text) for term in terms)


def _detect_language(lowered: str) -> str:
    hinglish_terms = {
        "aaj",
        "aaya",
        "aaye",
        "diya",
        "hua",
        "kaam",
        "ke",
        "liye",
        "mazdoor",
        "mein",
        "me",
        "par",
    }
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
    for canonical, aliases in ACTIVITY_ALIASES.items():
        for alias in sorted(aliases, key=len, reverse=True):
            if re.search(rf"\b{re.escape(alias)}\b", lowered):
                return canonical
    return None


def _extract_material(lowered: str) -> str | None:
    for canonical, aliases in MATERIAL_ALIASES.items():
        for alias in sorted(aliases, key=len, reverse=True):
            if re.search(rf"\b{re.escape(alias)}\b", lowered):
                return canonical
    return None


def _extract_trades(lowered: str) -> dict[str, int]:
    trades: dict[str, int] = {}
    for canonical, aliases in TRADE_ALIASES.items():
        for alias in sorted(aliases, key=len, reverse=True):
            count = _extract_trade_count(lowered, alias)
            if count is not None:
                trades[canonical] = count
                break
    return trades


def _build_summary(title: str, extracted: dict, missing: list[str]) -> str:
    if missing:
        missing_text = ", ".join(_humanize_field(field) for field in missing)
        return f"I understood this as {title.lower()}, but I still need {missing_text}."

    if title == "Progress":
        activity = extracted.get("activity")
        quantity = _format_quantity(extracted.get("quantity"))
        unit = extracted.get("unit")
        location = extracted.get("location")
        return f"I read this as progress: {activity}, {quantity} {unit} at {location}."

    if title == "Manpower":
        trade_counts = _format_trade_counts(extracted.get("trade_counts") or {})
        location = extracted.get("location")
        return f"I read this as manpower: {trade_counts} at {location}."

    if title in {"Material received", "Material issued"}:
        material = extracted.get("material")
        quantity = _format_quantity(extracted.get("quantity"))
        unit = extracted.get("unit")
        location = extracted.get("location")
        location_text = f" at {location}" if location else ""
        return f"I read this as {title.lower()}: {quantity} {unit} of {material}{location_text}."

    return f"I understood this as {title.lower()}."


def _extract_trade_count(lowered: str, trade: str) -> int | None:
    before_trade = re.search(rf"\b(\d+)\s+{re.escape(trade)}s?\b", lowered)
    if before_trade:
        return int(before_trade.group(1))

    after_trade = re.search(rf"\b{re.escape(trade)}s?\s*(?:is|are|=|:)?\s*(\d+)\b", lowered)
    if after_trade:
        return int(after_trade.group(1))

    return None


def _format_trade_counts(trade_counts: dict[str, int]) -> str:
    return ", ".join(
        f"{count} {trade}" for trade, count in sorted(trade_counts.items())
    )


def _format_quantity(value: object) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _humanize_field(field: str) -> str:
    labels = {
        "activity": "the activity or work item",
        "intent": "the type of update",
        "location": "the location or area",
        "material": "the material name",
        "message_text": "the message text",
        "quantity": "the quantity",
        "trade_counts": "the worker count by trade",
        "unit": "the unit",
    }
    return labels.get(field, field.replace("_", " "))
