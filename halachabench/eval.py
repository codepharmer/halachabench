import argparse
import sys
from typing import Any, Dict

from .constants import DEFAULT_NUMERIC_TOLERANCE
from .io_utils import read_jsonl, read_predictions, write_json
from .report import build_report, format_summary
from .schema import validate_questions
from .scoring import ScoreDetail, score_question


def evaluate(
    questions: list[Dict[str, Any]],
    predictions: Dict[str, Any],
    default_numeric_tolerance: float,
    include_per_question: bool = False,
) -> Dict[str, Any]:
    score_details: Dict[str, ScoreDetail] = {}
    for question in questions:
        qid = question["question_id"]
        prediction = predictions.get(qid)
        score_details[qid] = score_question(
            question, prediction, default_numeric_tolerance=default_numeric_tolerance
        )

    report = build_report(questions, score_details)
    if include_per_question:
        report["per_question"] = [
            {
                "question_id": qid,
                "score": detail.score,
                "max_score": detail.max_score,
                "is_correct": detail.is_correct,
                "error": detail.error,
            }
            for qid, detail in score_details.items()
        ]
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate HalachaBench predictions.")
    parser.add_argument(
        "--questions",
        required=True,
        help="Path to questions JSONL file.",
    )
    parser.add_argument(
        "--predictions",
        required=False,
        help="Path to predictions JSONL file.",
    )
    parser.add_argument(
        "--out",
        help="Optional path to write the full JSON report.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output to --out.",
    )
    parser.add_argument(
        "--per-question",
        action="store_true",
        help="Include per-question scoring details in the output report.",
    )
    parser.add_argument(
        "--default-numeric-tolerance",
        type=float,
        default=DEFAULT_NUMERIC_TOLERANCE,
        help="Fallback numeric tolerance if a question does not specify one.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate questions and exit.",
    )

    args = parser.parse_args()
    questions = read_jsonl(args.questions)
    errors = validate_questions(questions)
    if errors:
        for err in errors:
            prefix = err.question_id or "<unknown>"
            print(f"Validation error [{prefix}]: {err.message}", file=sys.stderr)
        if args.validate_only:
            return 1

    if args.validate_only:
        print("Validation passed.")
        return 0

    if not args.predictions:
        print("--predictions is required unless --validate-only is set.", file=sys.stderr)
        return 2

    predictions = read_predictions(args.predictions)
    report = evaluate(
        questions,
        predictions,
        default_numeric_tolerance=args.default_numeric_tolerance,
        include_per_question=args.per_question,
    )

    print(format_summary(report))

    if args.out:
        write_json(args.out, report, pretty=args.pretty)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
