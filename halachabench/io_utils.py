import json
from typing import Any, Dict, Iterable, List


def read_jsonl(path: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON on line {line_no} in {path}: {exc}") from exc
    return records


def write_json(path: str, payload: Any, pretty: bool = True) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        if pretty:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        else:
            json.dump(payload, handle, ensure_ascii=False, separators=(",", ":"))


def read_predictions(path: str) -> Dict[str, Any]:
    predictions: Dict[str, Any] = {}
    with open(path, "r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON on line {line_no} in {path}: {exc}") from exc
            question_id = record.get("question_id")
            if not question_id:
                raise ValueError(f"missing question_id on line {line_no} in {path}")
            answer = record.get("answer")
            if answer is None and "prediction" in record:
                answer = record.get("prediction")
            predictions[question_id] = answer
    return predictions