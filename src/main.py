import argparse
import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path

from src.reviewer import DeepSeekReviewer


def to_dict(obj):
    """兼容 dataclass、Pydantic 和普通对象。"""
    if is_dataclass(obj):
        return asdict(obj)

    if hasattr(obj, "model_dump"):
        return obj.model_dump()

    if hasattr(obj, "dict"):
        return obj.dict()

    if hasattr(obj, "__dict__"):
        return vars(obj)

    return obj


def main():
    parser = argparse.ArgumentParser(
        description="OpenHands CodeReview Agent - review a Git diff"
    )
    parser.add_argument(
        "--diff",
        required=True,
        help="Path to a unified Git diff file",
    )
    args = parser.parse_args()

    diff_path = Path(args.diff)

    if not diff_path.exists():
        print(f"ERROR: Diff file not found: {diff_path}", file=sys.stderr)
        return 1

    diff_text = diff_path.read_text(encoding="utf-8")

    if not diff_text.strip():
        print("ERROR: Diff file is empty.", file=sys.stderr)
        return 1

    try:
        reviewer = DeepSeekReviewer()
        result, validation = reviewer.review_and_validate(diff_text)

        output = {
            "review_result": to_dict(result),
            "validation_result": to_dict(validation),
        }

        print(json.dumps(output, ensure_ascii=False, indent=2, default=str))
        return 0

    except Exception as exc:
        print(f"Code review failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

