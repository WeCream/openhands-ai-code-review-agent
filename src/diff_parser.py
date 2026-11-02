from dataclasses import dataclass, field
from typing import Literal
import re


@dataclass
class DiffLine:
    kind: Literal["context", "added", "removed"]
    content: str
    old_line: int | None
    new_line: int | None


@dataclass
class FileDiff:
    old_path: str | None
    new_path: str | None
    lines: list[DiffLine] = field(default_factory=list)


def _clean_path(path: str) -> str | None:
    path = path.strip()
    if path == "/dev/null":
        return None
    if path.startswith(("a/", "b/")):
        return path[2:]
    return path


def parse_diff(diff_text: str) -> list[FileDiff]:
    """解析常见 unified Git diff，保留新旧行号和文件重命名路径。"""
    files: list[FileDiff] = []
    current: FileDiff | None = None
    old_line: int | None = None
    new_line: int | None = None

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            current = FileDiff(old_path=None, new_path=None)
            files.append(current)
            old_line = None
            new_line = None

            # 从 diff --git 头部提取初始路径。
            # 复杂的带空格路径以 --- / +++ 头或 rename 元数据为准。
            match = re.match(r"diff --git a/(.+) b/(.+)$", line)
            if match:
                current.old_path = match.group(1)
                current.new_path = match.group(2)
            continue

        if current is None:
            continue

        if line.startswith("rename from "):
            current.old_path = line[len("rename from "):]
            continue

        if line.startswith("rename to "):
            current.new_path = line[len("rename to "):]
            continue

        if line.startswith("--- "):
            current.old_path = _clean_path(line[4:])
            continue

        if line.startswith("+++ "):
            current.new_path = _clean_path(line[4:])
            continue

        if line.startswith("@@ "):
            match = re.match(
                r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@",
                line,
            )
            if not match:
                old_line = None
                new_line = None
                continue

            old_line = int(match.group(1))
            new_line = int(match.group(2))
            continue

        if line.startswith("\\ No newline at end of file"):
            continue

        if old_line is None or new_line is None:
            continue

        if line.startswith("+"):
            current.lines.append(
                DiffLine("added", line[1:], None, new_line)
            )
            new_line += 1
        elif line.startswith("-"):
            current.lines.append(
                DiffLine("removed", line[1:], old_line, None)
            )
            old_line += 1
        elif line.startswith(" "):
            current.lines.append(
                DiffLine("context", line[1:], old_line, new_line)
            )
            old_line += 1
            new_line += 1

    return files
