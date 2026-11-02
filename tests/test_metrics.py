import unittest

from src.metrics import calculate_metrics


class TestCalculateMetrics(unittest.TestCase):
    def test_strict_metrics_use_documented_granularity(self):
        results = [
            {"expected_issue": True, "detected": True, "strict_detected": True,
             "valid_finding_count": 2, "finding_count": 2, "issue_type_match_count": 1},
            {"expected_issue": True, "detected": True, "strict_detected": False,
             "valid_finding_count": 1, "finding_count": 2, "issue_type_match_count": 0},
            {"expected_issue": False, "detected": True, "strict_detected": False,
             "valid_finding_count": 1, "finding_count": 1, "issue_type_match_count": 0},
            {"expected_issue": False, "detected": False, "strict_detected": False,
             "valid_finding_count": 0, "finding_count": 0, "issue_type_match_count": 0},
        ]
        metrics = calculate_metrics(results)
        self.assertEqual(metrics["strict_TP"], 1)
        self.assertEqual(metrics["strict_FN"], 1)
        self.assertEqual(metrics["strict_FP"], 1)
        self.assertEqual(metrics["strict_TN"], 1)
        self.assertEqual(metrics["strict_recall"], 0.5)
        self.assertEqual(metrics["strict_precision"], 1 / 4)
        self.assertEqual(metrics["evidence_pass_rate"], 4 / 5)

    def test_empty_results_return_none_for_rates(self):
        metrics = calculate_metrics([])
        for key in ("recall", "precision", "false_positive_rate", "accuracy",
                    "strict_recall", "strict_precision", "evidence_pass_rate"):
            self.assertIsNone(metrics[key], key)


if __name__ == "__main__":
    unittest.main()
