from src.openhands_adapter.code_review_tool import (
    CodeReviewAction,
    CodeReviewExecutor,
)


class MockReviewResult:
    def model_dump(self, mode="json"):
        return {
            "summary": "发现一个潜在问题",
            "findings": [
                {
                    "title": "除零风险",
                    "severity": "high",
                    "file_path": "app.py",
                    "line": 10,
                    "description": "可能发生除零错误",
                    "evidence": "return total / count",
                    "suggestion": "除法前检查 count 是否为 0",
                    "issue_type": "bug",
                }
            ],
        }


class MockValidationResult:
    def model_dump(self, mode="json"):
        return {
            "valid": True,
            "invalid_findings": [],
        }


class MockReviewer:
    def review_and_validate(self, diff_text):
        assert "return total / count" in diff_text

        return (
            MockReviewResult(),
            MockValidationResult(),
        )


def test_code_review_executor():
    reviewer = MockReviewer()
    executor = CodeReviewExecutor(reviewer=reviewer)

    action = CodeReviewAction(
        diff_text="diff --git a/app.py b/app.py\n"
        "+return total / count\n"
    )

    observation = executor(action)

    assert observation.summary == "发现一个潜在问题"
    assert observation.finding_count == 1

    assert observation.review_result["findings"][0]["title"] == "除零风险"

    assert observation.validation_result["valid"] is True

    print("Mock CodeReviewExecutor test passed!")