# 2026-02-05 Seed Release

This release is a seed dataset for the evaluation harness. It is intentionally small and includes
synthetic/illustrative questions meant to exercise scoring rules. The questions are **not** halachic
guidance and should not be used for decision making.

## Contents

- questions.jsonl: Seed questions with explicit attribution and licenses.

## Notes

- Question IDs are deterministic hashes of canonical question content.
- Numeric questions may include a per-question `tolerance` and optional `tolerance_type`.