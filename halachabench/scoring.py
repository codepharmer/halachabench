from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .normalize import normalize_text, parse_boolean, parse_json, parse_numeric


@dataclass
class ScoreDetail:
    question_id: str
    score: float
    max_score: float
    is_correct: bool
    error: Optional[str] = None


def _resolve_mcq_value(value: Any, choices: List[Any]) -> Any:
    if isinstance(value, int) and 0 <= value < len(choices):
        return choices[value]
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.isdigit():
            idx = int(stripped)
            if 0 <= idx < len(choices):
                return choices[idx]
    return value


def _build_acceptable_answers(question: Dict[str, Any]) -> List[Any]:
    acceptable = question.get("acceptable_answers")
    if acceptable is None:
        acceptable = [question.get("ground_truth")]
    if not isinstance(acceptable, list):
        acceptable = [acceptable]
    return acceptable


def score_question(
    question: Dict[str, Any],
    prediction: Any,
    default_numeric_tolerance: float = 0.0,
) -> ScoreDetail:
    qid = question.get("question_id", "")
    if prediction is None:
        return ScoreDetail(qid, 0.0, 1.0, False, error="missing_prediction")

    answer_type = question.get("answer_type")
    ground_truth = question.get("ground_truth")

    if answer_type in {"enum", "mcq"}:
        choices = question.get("choices") if answer_type == "mcq" else None
        acceptable = _build_acceptable_answers(question)
        if choices:
            acceptable = [_resolve_mcq_value(item, choices) for item in acceptable]
            prediction = _resolve_mcq_value(prediction, choices)
        normalized_prediction = normalize_text(prediction)
        normalized_acceptable = {normalize_text(item) for item in acceptable}
        is_correct = normalized_prediction is not None and normalized_prediction in normalized_acceptable
        return ScoreDetail(qid, 1.0 if is_correct else 0.0, 1.0, is_correct)

    if answer_type == "boolean":
        pred_value = parse_boolean(prediction)
        truth_value = parse_boolean(ground_truth)
        if pred_value is None or truth_value is None:
            return ScoreDetail(qid, 0.0, 1.0, False, error="invalid_boolean")
        is_correct = pred_value == truth_value
        return ScoreDetail(qid, 1.0 if is_correct else 0.0, 1.0, is_correct)

    if answer_type == "numeric":
        pred_value = parse_numeric(prediction)
        truth_value = parse_numeric(ground_truth)
        if pred_value is None or truth_value is None:
            return ScoreDetail(qid, 0.0, 1.0, False, error="invalid_numeric")
        tolerance = question.get("tolerance", default_numeric_tolerance)
        tolerance_type = question.get("tolerance_type", "absolute")
        if tolerance_type == "relative" and truth_value != 0:
            threshold = abs(truth_value) * float(tolerance)
        else:
            threshold = float(tolerance)
        is_correct = abs(pred_value - truth_value) <= threshold
        return ScoreDetail(qid, 1.0 if is_correct else 0.0, 1.0, is_correct)

    if answer_type == "json":
        pred_value = parse_json(prediction)
        truth_value = parse_json(ground_truth)
        if pred_value is None or truth_value is None:
            return ScoreDetail(qid, 0.0, 1.0, False, error="invalid_json")
        is_correct = pred_value == truth_value
        return ScoreDetail(qid, 1.0 if is_correct else 0.0, 1.0, is_correct)

    return ScoreDetail(qid, 0.0, 1.0, False, error="unsupported_answer_type")