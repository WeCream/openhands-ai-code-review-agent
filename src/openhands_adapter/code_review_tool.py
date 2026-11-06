
from dataclasses import asdict, is_dataclass
from collections.abc import Sequence
from typing import Any

from pydantic import Field

from openhands.sdk import (
    Action,
    Observation,
    TextContent,
    ImageContent,
    ToolDefinition,
)
from openhands.sdk.tool import ToolExecutor

from src.reviewer import DeepSeekReviewer


# =========================================================
# 1. Action：LLM 发起代码审查时提供的参数
# =========================================================

class CodeReviewAction(Action):
    diff_text: str = Field(
        description=(
            "Unified Git diff to review. "
            "Provide the complete diff text."
        ),
        min_length=1,
    )


# =========================================================
# 2. Observation：代码审查完成后返回给 Agent 的结果
# =========================================================

class CodeReviewObservation(Observation):
    summary: str = ""
    finding_count: int = 0

    # 保留原始结构化审查结果
    review_result: dict[str, Any] = Field(
        default_factory=dict
    )

    # 保留 evidence validation 结果
    validation_result: dict[str, Any] = Field(
        default_factory=dict
    )

    @property
    def to_llm_content(
        self,
    ) -> Sequence[TextContent | ImageContent]:
        """将结构化结果转换成 LLM 能理解的文本。"""

        lines = [
            "Code review completed.",
            f"Summary: {self.summary}",
            f"Finding count: {self.finding_count}",
        ]

        findings = self.review_result.get(
            "findings", []
        )

        for index, finding in enumerate(findings, 1):
            lines.extend([
                "",
                f"Finding #{index}",
                f"Title: {finding.get('title', '')}",
                f"Severity: {finding.get('severity', '')}",
                (
                    "Location: "
                    f"{finding.get('file_path', '')}:"
                    f"{finding.get('line', '')}"
                ),
                (
                    "Description: "
                    f"{finding.get('description', '')}"
                ),
                f"Evidence: {finding.get('evidence', '')}",
                (
                    "Suggestion: "
                    f"{finding.get('suggestion', '')}"
                ),
            ])

        lines.extend([
            "",
            "Evidence validation:",
            str(self.validation_result),
        ])

        return [
            TextContent(text="\n".join(lines))
        ]

def _to_dict(obj):
    """将 dataclass 或普通对象转换为字典。"""
    if is_dataclass(obj):
        return asdict(obj)

    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")

    if hasattr(obj, "dict"):
        return obj.dict()

    if hasattr(obj, "__dict__"):
        return vars(obj)

    raise TypeError(f"Unsupported object type: {type(obj).__name__}")
# =========================================================
# 3. Executor：调用现有 Reviewer
# =========================================================

class CodeReviewExecutor(
    ToolExecutor[CodeReviewAction, CodeReviewObservation]
):
    def __init__(self, reviewer: DeepSeekReviewer | None = None):
        # 允许注入 Mock Reviewer，也允许延迟初始化真实 Reviewer
        self.reviewer = reviewer

    def __call__(
        self,
        action: CodeReviewAction,
        conversation=None,
    ) -> CodeReviewObservation:
        # 真正执行审查时，才初始化 DeepSeek Reviewer
        reviewer = self.reviewer

        if reviewer is None:
            reviewer = DeepSeekReviewer()

        review_result, validation_result = (
            reviewer.review_and_validate(action.diff_text)
        )
        review_data = _to_dict(review_result)
        validation_data = _to_dict(validation_result)

        return CodeReviewObservation(
            summary=review_data.get("summary", ""),
            finding_count=len(review_data.get("findings", [])),
            review_result=review_data,
            validation_result=validation_data,
        )
# =========================================================
# 4. ToolDefinition：将 Action、Observation、Executor 组装
# =========================================================

class CodeReviewTool(
    ToolDefinition[
        CodeReviewAction,
        CodeReviewObservation,
    ]
):
    @classmethod
    def create(
        cls,
        conv_state,
        **params,
    ) -> Sequence[ToolDefinition]:

        executor = CodeReviewExecutor()
        return [
            cls(
                description=(
                    "Review a unified Git diff for bugs, "
                    "security vulnerabilities, and "
                    "maintainability issues. "
                    "Use this tool when the user requests "
                    "a code review. Provide the diff text."
                ),
                action_type=CodeReviewAction,
                observation_type=CodeReviewObservation,
                executor=executor,
            )
        ]