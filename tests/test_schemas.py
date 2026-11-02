
import unittest

from src.schemas import ReviewFinding, ReviewResult


def make_finding(**overrides):
    data = {
        "title": "Potential null access",
        "severity": "high",
        "file_path": "src/example.py",
        "line": 12,
        "description": "The value may be None.",
        "evidence": "user.name",
        "suggestion": "Check user before accessing name.",
        "issue_type": "division_by_zero",
    }
    data.update(overrides)
    return ReviewFinding(**data)


class TestReviewSchemas(unittest.TestCase):
    def test_valid_finding(self):
        finding = make_finding()
        self.assertEqual(finding.severity, "high")
        self.assertEqual(finding.line, 12)

    def test_invalid_severity(self):
        with self.assertRaises(ValueError):
            make_finding(severity="urgent")

    def test_invalid_line(self):
        with self.assertRaises(ValueError):
            make_finding(line=0)

    def test_empty_evidence(self):
        with self.assertRaises(ValueError):
            make_finding(evidence=" ")

    def test_review_result_count(self):
        result = ReviewResult(
            summary="One potential issue found.",
            findings=[make_finding()],
        )
        self.assertEqual(result.finding_count, 1)

    def test_result_rejects_wrong_finding_type(self):
        with self.assertRaises(ValueError):
            ReviewResult(summary="Review complete.", findings=["not a finding"])


if __name__ == "__main__":
    unittest.main()
