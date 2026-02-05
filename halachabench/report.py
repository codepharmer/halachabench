from collections import defaultdict
from typing import Any, Dict, Iterable, List, Tuple

from .scoring import ScoreDetail


def _mean(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def build_report(
    questions: Iterable[Dict[str, Any]],
    score_details: Dict[str, ScoreDetail],
) -> Dict[str, Any]:
    task_scores: Dict[Tuple[str, str], List[float]] = defaultdict(list)
    task_counts: Dict[Tuple[str, str], int] = defaultdict(int)
    missing = 0

    for question in questions:
        qid = question["question_id"]
        detail = score_details[qid]
        if detail.error == "missing_prediction":
            missing += 1
        key = (question["category"], question["task"])
        task_scores[key].append(detail.score)
        task_counts[key] += 1

    task_results: Dict[str, Dict[str, Any]] = {}
    category_tasks: Dict[str, List[float]] = defaultdict(list)
    category_task_details: Dict[str, Dict[str, Any]] = defaultdict(dict)

    for (category, task), scores in task_scores.items():
        score = _mean(scores)
        task_key = f"{category}::{task}"
        task_results[task_key] = {
            "category": category,
            "task": task,
            "score": score,
            "n_questions": task_counts[(category, task)],
        }
        category_tasks[category].append(score)
        category_task_details[category][task] = {
            "score": score,
            "n_questions": task_counts[(category, task)],
        }

    category_results: Dict[str, Any] = {}
    for category, scores in category_tasks.items():
        category_results[category] = {
            "score": _mean(scores),
            "tasks": category_task_details[category],
            "n_tasks": len(scores),
        }

    overall = _mean([cat["score"] for cat in category_results.values()])

    report = {
        "overall": overall,
        "categories": category_results,
        "tasks": task_results,
        "n_questions": sum(task_counts.values()),
        "n_missing": missing,
    }
    return report


def format_summary(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(
        f"Overall: {report['overall']:.3f} (questions: {report['n_questions']}, missing: {report['n_missing']})"
    )
    for category, payload in sorted(report["categories"].items()):
        lines.append(
            f"{category}: {payload['score']:.3f} (tasks: {payload['n_tasks']})"
        )
        for task, detail in sorted(payload["tasks"].items()):
            lines.append(
                f"  {task}: {detail['score']:.3f} (n: {detail['n_questions']})"
            )
    return "\n".join(lines)
