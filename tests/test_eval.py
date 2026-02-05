import json
import unittest

from halachabench.eval import evaluate
from halachabench.io_utils import read_jsonl, read_predictions


class TestEvaluation(unittest.TestCase):
    def test_sample_predictions_score_one(self):
        questions = read_jsonl("data/releases/2026-02-05/questions.jsonl")
        predictions = read_predictions("examples/predictions.sample.jsonl")
        report = evaluate(questions, predictions, default_numeric_tolerance=0.0)
        self.assertAlmostEqual(report["overall"], 1.0, places=6)


if __name__ == "__main__":
    unittest.main()