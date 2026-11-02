from src.evidence_validator import ValidationResult
from src.schemas import ReviewResult


def _format_finding(finding, number: int) -> list[str]:
    """将一条审查发现格式化为 Markdown。"""

    return [
        f"### {number}. {finding.title}",
        "",
        f"- **严重程度：** `{finding.severity.upper()}`",
        f"- **代码位置：** `{finding.file_path}:{finding.line}`",
        f"- **问题说明：** {finding.description}",
        f"- **代码证据：** `{finding.evidence}`",
        f"- **修复建议：** {finding.suggestion}",
        "",
    ]


def generate_markdown_report(
    result: ReviewResult,
    validation: ValidationResult,
) -> str:
    """根据审查结果和证据校验结果生成 Markdown 报告。"""

    valid_count = len(validation.valid_findings)
    invalid_count = len(validation.invalid_findings)
    total_count = valid_count + invalid_count

    lines = [
        "# Code Review Report",
        "",
        "## 1. 审查摘要",
        "",
        result.summary,
        "",
        f"- **发现总数：** {total_count}",
        f"- **通过证据校验：** {valid_count}",
        f"- **未通过证据校验：** {invalid_count}",
        "",
        "> 说明：通过证据校验仅表示文件、行号和代码证据满足当前校验规则，",
        "> 不代表问题在逻辑上一定成立。",
        "",
        "## 2. 通过证据校验的问题",
        "",
    ]

    if validation.valid_findings:
        for index, finding in enumerate(validation.valid_findings, start=1):
            lines.extend(_format_finding(finding, index))
    else:
        lines.extend(["暂无通过证据校验的问题。", ""])

    lines.extend([
        "## 3. 未通过证据校验的问题",
        "",
    ])

    if validation.invalid_findings:
        for index, issue in enumerate(validation.invalid_findings, start=1):
            finding = issue.finding

            lines.extend([
                f"### {index}. {finding.title}",
                "",
                f"- **严重程度：** `{finding.severity.upper()}`",
                f"- **模型报告的位置：** `{finding.file_path}:{finding.line}`",
                f"- **未通过原因：** {issue.reason}",
                f"- **问题说明：** {finding.description}",
                f"- **模型提供的证据：** `{finding.evidence}`",
                f"- **修复建议：** {finding.suggestion}",
                "",
            ])
    else:
        lines.extend(["暂无未通过证据校验的问题。", ""])

    lines.extend([
        "---",
        "",
        "*本报告由 OpenHands CodeReview Agent 生成。*",
        "",
    ])

    return "\n".join(lines)