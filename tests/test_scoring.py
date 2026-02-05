import unittest

from halachabench.normalize import normalize_text, parse_boolean, parse_numeric
from halachabench.scoring import score_question


class TestScoring(unittest.TestCase):
    def test_normalize_text(self):
        self.assertEqual(normalize_text(" HaMotzi! "), "hamotzi")

    def test_boolean_parse(self):
        self.assertTrue(parse_boolean("Yes"))
        self.assertFalse(parse_boolean("0"))

    def test_numeric_tolerance(self):
        question = {
            "question_id": "q1",
            "answer_type": "numeric",
            "ground_truth": 100,
            "tolerance": 2,
        }
        detail = score_question(question, 101)
        self.assertTrue(detail.is_correct)
        detail = score_question(question, 103)
        self.assertFalse(detail.is_correct)

    def test_mcq_index(self):
        question = {
            "question_id": "q2",
            "answer_type": "mcq",
            "ground_truth": "B",
            "choices": ["A", "B", "C"],
        }
        detail = score_question(question, 1)
        self.assertTrue(detail.is_correct)


if __name__ == "__main__":
    unittest.main()