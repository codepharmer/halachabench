import json
import re
import unicodedata
from typing import Any, Optional


_WHITESPACE_RE = re.compile(r"\s+")


def _strip_punct_and_symbols(text: str) -> str:
    # Remove unicode punctuation and symbols while keeping letters and numbers.
    return "".join(
        ch
        for ch in text
        if unicodedata.category(ch)[0] not in ("P", "S")
    )


def normalize_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    value = unicodedata.normalize("NFKC", value)
    value = value.casefold().strip()
    value = _strip_punct_and_symbols(value)
    value = _WHITESPACE_RE.sub(" ", value).strip()
    return value or None


def parse_boolean(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if value == 1:
            return True
        if value == 0:
            return False
    if isinstance(value, str):
        normalized = normalize_text(value)
        if normalized in {"true", "t", "yes", "y", "1"}:
            return True
        if normalized in {"false", "f", "no", "n", "0"}:
            return False
    return None


def parse_numeric(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "")
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def parse_json(value: Any) -> Optional[Any]:
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None
    return None