
from dataclasses import dataclass, field
from typing import Literal


Severity = Literal["critical", "high", "medium", "low", "info"]

IssueType = Literal[
    "division_by_zero",
    "index_out_of_range",
    "none_attribute_access",
    "resource_leak",
    "sql_injection",
    "sensitive_data_logging",
    "incorrect_error_fallback",
    "command_injection",
    "no_issue",
]

VALID_SEVERITIES = {"critical", "high", "medium", "low", "info"}

VALID_ISSUE_TYPES = {
    "division_by_zero",
    "index_out_of_range",
    "none_attribute_access",
    "resource_leak",
    "sql_injection",
    "sensitive_data_logging",
    "incorrect_error_fallback",
    "command_injection",
    "no_issue",
}


@dataclass
class ReviewFinding:
    """一条代码审查发现。"""

    title: str
    severity: Severity
    file_path: str
    line: int
    description: str
    evidence: str
    suggestion: str
    issue_type: IssueType

    def __post_init__(self) -> None:
        required_text = {
            "title": self.title,
            "file_path": self.file_path,
            "description": self.description,
            "evidence": self.evidence,
            "suggestion": self.suggestion,
        }

        for field_name, value in required_text.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")

        if self.severity not in VALID_SEVERITIES:
            raise ValueError(f"Invalid severity: {self.severity}")

        if self.issue_type not in VALID_ISSUE_TYPES:
            raise ValueError(f"Invalid issue_type: {self.issue_type}")

        if isinstance(self.line, bool) or not isinstance(self.line, int) or self.line < 1:
            raise ValueError("line must be a positive integer")


@dataclass
class ReviewResult:
    """一次代码审查的结构化结果。"""

    summary: str
    findings: list[ReviewFinding] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.summary, str) or not self.summary.strip():
            raise ValueError("summary must be a non-empty string")

        if not isinstance(self.findings, list):
            raise ValueError("findings must be a list")

        if not all(isinstance(item, ReviewFinding) for item in self.findings):
            raise ValueError("every finding must be a ReviewFinding")

    @property
    def finding_count(self) -> int:
        return len(self.findings)
