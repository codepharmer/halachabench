import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .constants import ALLOWED_ANSWER_TYPES, ALLOWED_ROLES


@dataclass(frozen=True)
class ValidationError:
    question_id: Optional[str]
    message: str


def _canonicalize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _canonicalize_value(value[key]) for key in sorted(value.keys())}
    if isinstance(value, list):
        return [_canonicalize_value(item) for item in value]
    return value


def canonical_question_json(question: Dict[str, Any]) -> str:
    canonical = {key: question[key] for key in question if key != "question_id"}
    canonical = _canonicalize_value(canonical)
    return json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_question_id(question: Dict[str, Any]) -> str:
    canonical_json = canonical_question_json(question)
    digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    return digest


def validate_question(question: Dict[str, Any]) -> List[ValidationError]:
    errors: List[ValidationError] = []
    qid = question.get("question_id")

    required_fields = [
        "question_id",
        "category",
        "task",
        "turns",
        "answer_type",
        "ground_truth",
        "release_date",
        "license",
        "attribution",
    ]

    for field in required_fields:
        if field not in question:
            errors.append(ValidationError(qid, f"missing required field: {field}"))

    answer_type = question.get("answer_type")
    if answer_type and answer_type not in ALLOWED_ANSWER_TYPES:
        errors.append(ValidationError(qid, f"invalid answer_type: {answer_type}"))

    turns = question.get("turns")
    if not isinstance(turns, list) or not turns:
        errors.append(ValidationError(qid, "turns must be a non-empty list"))
    else:
        for idx, turn in enumerate(turns):
            if not isinstance(turn, dict):
                errors.append(ValidationError(qid, f"turns[{idx}] must be an object"))
                continue
            role = turn.get("role")
            content = turn.get("content")
            if role not in ALLOWED_ROLES:
                errors.append(ValidationError(qid, f"turns[{idx}].role invalid: {role}"))
            if not isinstance(content, str) or not content.strip():
                errors.append(ValidationError(qid, f"turns[{idx}].content must be a non-empty string"))

    release_date = question.get("release_date")
    if release_date:
        try:
            datetime.strptime(release_date, "%Y-%m-%d")
        except ValueError:
            errors.append(ValidationError(qid, "release_date must be YYYY-MM-DD"))

    if answer_type == "mcq":
        choices = question.get("choices")
        if not isinstance(choices, list) or not choices:
            errors.append(ValidationError(qid, "mcq requires non-empty choices list"))

    if answer_type == "numeric":
        tolerance = question.get("tolerance")
        if tolerance is not None and not isinstance(tolerance, (int, float)):
            errors.append(ValidationError(qid, "tolerance must be numeric if provided"))

    if "question_id" in question:
        expected = compute_question_id(question)
        if question["question_id"] != expected:
            errors.append(
                ValidationError(
                    qid,
                    "question_id does not match canonical hash",
                )
            )

    return errors


def validate_questions(questions: Iterable[Dict[str, Any]]) -> List[ValidationError]:
    errors: List[ValidationError] = []
    for question in questions:
        errors.extend(validate_question(question))
    return errors