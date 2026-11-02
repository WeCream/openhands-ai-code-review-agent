
from dataclasses import dataclass

from src.diff_parser import FileDiff, parse_diff
from src.schemas import ReviewFinding, ReviewResult


@dataclass
class ValidationIssue:
    """一条审查发现的校验问题。"""

    finding: ReviewFinding
    reason: str


@dataclass
class ValidationResult:
    """证据校验的整体结果。"""

    valid_findings: list[ReviewFinding]
    invalid_findings: list[ValidationIssue]

    @property
    def is_valid(self) -> bool:
        return len(self.invalid_findings) == 0


def _normalize_path(path: str) -> str:
    """统一常见路径分隔符，方便比较。"""
    return path.replace("\\", "/").removeprefix("./")


def _find_file(
    finding_path: str,
    files: list[FileDiff],
) -> FileDiff | None:
    """根据审查报告中的路径查找对应文件。"""
    target = _normalize_path(finding_path)

    for file_diff in files:
        if file_diff.new_path is None:
            continue

        if _normalize_path(file_diff.new_path) == target:
            return file_diff

    return None

def locate_finding_line(
    finding: ReviewFinding,
    files: list[FileDiff],
) -> int | None:
    """根据证据内容定位唯一新增行，无法唯一定位时返回 None。"""

    file_diff = _find_file(finding.file_path, files)

    if file_diff is None:
        return None

    evidence = finding.evidence.strip()

    if not evidence:
        return None

    matches = [
        line.new_line
        for line in file_diff.lines
        if (
            line.kind == "added"
            and line.new_line is not None
            and evidence in line.content
        )
    ]

    # 只接受唯一匹配，防止把证据定位到错误行。
    if len(matches) == 1:
        return matches[0]

    return None

def validate_finding(
    finding: ReviewFinding,
    files: list[FileDiff],
) -> str | None:
    """
    校验单条发现。

    返回 None 表示通过；返回字符串表示校验失败的原因。
    第一版只接受新增代码行作为问题位置。
    """

    file_diff = _find_file(finding.file_path, files)

    if file_diff is None:
        return f"File not found in diff: {finding.file_path}"

    added_lines = [
        line
        for line in file_diff.lines
        if line.kind == "added"
    ]

    matching_line = next(
        (
            line
            for line in added_lines
            if line.new_line == finding.line
        ),
        None,
    )

    if matching_line is None:
        return (
            f"Line {finding.line} is not an added line "
            f"in {finding.file_path}"
        )

    evidence = finding.evidence.strip()

    if not evidence:
        return "Evidence must not be empty"

    # 证据必须是该新增代码行内容的一部分。
    # 不允许只因为证据出现在其他文件或其他行就通过。
    if evidence not in matching_line.content:
        return (
            f"Evidence does not match line {finding.line} "
            f"in {finding.file_path}"
        )

    return None


def validate_review(
    diff_text: str,
    result: ReviewResult,
) -> ValidationResult:
    """校验整份审查结果，分离有效和无效发现。"""

    files = parse_diff(diff_text)

    valid_findings: list[ReviewFinding] = []
    invalid_findings: list[ValidationIssue] = []

    for finding in result.findings:
        located_line = locate_finding_line(finding, files)

        if located_line is not None:
            finding.line = located_line

        reason = validate_finding(finding, files)

        if reason is None:
            valid_findings.append(finding)
        else:
            invalid_findings.append(
                ValidationIssue(
                    finding=finding,
                    reason=reason,
                )
            )

    return ValidationResult(
        valid_findings=valid_findings,
        invalid_findings=invalid_findings,
    )