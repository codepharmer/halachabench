# HalachaBench

HalachaBench is a LiveBench-inspired benchmark for halacha questions that are objectively scorable without a judge model. It focuses on closed-format answers, explicit source attribution, and reproducible evaluation.

**Status**
Work in progress. This repository currently captures the intended design and policies. Code, datasets, and a public leaderboard will be added incrementally.

**Disclaimer**
This project is for benchmarking only. It does not provide halachic guidance. Always consult qualified authorities and primary sources.

## Phase 1 Status (Implemented)

The harness MVP and a small seed dataset are now implemented. You can validate questions,
score predictions deterministically, and generate per-task and per-category reports.

## Design Goals

- Objective, deterministic scoring only (no judge model).
- Versioned releases to reduce contamination.
- Reproducible evaluation harness and public leaderboard artifacts.
- Explicit licensing and attribution for every source text and question.

## Scope

Initial categories and task types are planned to include:

- Shabbat and Yom Tov: carrying and melacha classification, muktzeh classification.
- Kashrut: milk/meat status, utensil and kashering rules, bishul and pas akum.
- Tefillah and Berachot: beracha selection, minyan and timing rules.
- Zmanim and calendrical (optional): computed time within tolerance, order-of-times logic.
- Sources and citation precision: siman and seif selection, source support selection.
- Hebrew comprehension (objective): structured extraction, paraphrase selection.

## Question Format

Questions are stored as JSONL with a minimal, explicit schema.

Required fields:

- `question_id` deterministic hash of canonical content.
- `category` category name.
- `task` task name.
- `turns` array of message turns used for evaluation.
- `answer_type` one of `mcq`, `boolean`, `enum`, `numeric`, `json`.
- `ground_truth` canonical answer.
- `release_date` in `YYYY-MM-DD`.
- `license` and `attribution` for the source text.

Optional fields:

- `choices` for multiple-choice tasks.
- `acceptable_answers` for multiple valid answers.
- `source_refs` structured references such as work, siman, and seif.
- `source_excerpt` for open-book tasks.

Example:

```json
{
  "question_id": "9f2a...c1",
  "category": "Kashrut",
  "task": "milk_meat_status",
  "turns": [
    {"role": "user", "content": "Is butter considered dairy or pareve?"}
  ],
  "answer_type": "enum",
  "ground_truth": "dairy",
  "acceptable_answers": ["dairy"],
  "source_refs": [{"work": "Shulchan Arukh", "siman": 87, "seif": 3}],
  "license": "CC-BY 4.0",
  "attribution": "Example Source",
  "release_date": "2026-02-05"
}
```

## Scoring

- Exact-match normalization for closed-form answers.
- Set-membership scoring for multiple acceptable answers.
- Numeric tolerance scoring for time-based or numeric questions.
- JSON schema validation for structured outputs.
- Task score is the mean of questions.
- Category score is the mean of tasks.
- Overall score is the mean of categories.

## Releases

- Versioned releases use `YYYY-MM-DD`.
- Rolling updates refresh a subset of questions each release.
- A private holdout split is maintained for official leaderboard scoring.

## Licensing Policy

- Source texts must be compatible with redistribution (PD, CC0, CC-BY, CC-BY-SA).
- Attribution and license metadata is stored with each question.
- No copyrighted translations without explicit permission.
- Prefer Hebrew or self-authored translations when needed.

## Planned Components

- Evaluation harness with a single end-to-end runner.
- OpenAI-compatible API interface for model connectivity.
- Public leaderboard artifacts with per-task and per-category breakdowns.
- Static frontend for browsing releases and model results.

## Getting Started

Requirements:

- Python 3.9+
- Node.js 18+ (for the Angular frontend)

Validate the seed release:

```bash
python -m halachabench.eval --questions data/releases/2026-02-05/questions.jsonl --validate-only
```

Score predictions:

```bash
python -m halachabench.eval \
  --questions data/releases/2026-02-05/questions.jsonl \
  --predictions examples/predictions.sample.jsonl \
  --out results.json \
  --pretty \
  --per-question
```

### Frontend (Angular)

The Angular app lives in `frontend/` and reads the seed release + sample report from `src/assets/`.

Run locally:

```bash
cd frontend
npm install
npm start
```

## Repository Layout

- `halachabench/`: evaluation harness (schema validation, scoring, reporting).
- `data/releases/2026-02-05/`: seed release JSONL and notes.
- `examples/`: sample predictions for quick evaluation runs.
- `frontend/`: Angular frontend that visualizes the seed release and sample report.
- `tests/`: unit tests for scoring and evaluation behavior.
- `examples/results.sample.json`: sample report output produced by the harness.

## Prediction Format

Predictions are JSONL with one record per question:

```json
{"question_id": "388a...", "answer": "dairy"}
```

Supported `answer` types are aligned with `answer_type`:

- `enum` / `mcq`: string or numeric index (for `mcq` with `choices`).
- `boolean`: true/false or yes/no.
- `numeric`: number or numeric string.
- `json`: JSON object or JSON-encoded string.

## Output Report

The evaluation report includes:

- `overall`: mean of category scores.
- `categories`: per-category score (mean of tasks).
- `tasks`: per-task score (mean of questions).
- `n_questions` and `n_missing` counts.

## Roadmap

- Phase 1: Harness MVP and seed dataset.
- Phase 2: Dataset pipeline, licensing enforcement, and release tooling.
- Phase 3: Frontend leaderboard and public artifacts.
- Phase 4: Monthly cadence with rolling refresh and holdout governance.

## Contributing

Contributions are welcome. If you want to propose a task or add questions:

- Open an issue describing the task and objective scoring rule.
- Provide source text references with explicit licensing.
- Include a small set of representative questions and ground-truth answers.
