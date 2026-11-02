import argparse
import sys
from pathlib import Path

from src.report import generate_markdown_report
from src.reviewer import DeepSeekReviewer, ReviewError


def main() -> int:
    parser = argparse.ArgumentParser(
        description="OpenHands CodeReview Agent - 审查 Git Diff 并生成报告"
    )
    parser.add_argument(
        "diff_file",
        help="待审查的 Git Diff 文件路径",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="review_report.md",
        help="报告输出路径，默认：review_report.md",
    )
    parser.add_argument(
        "--model",
        default="deepseek-chat",
        help="模型名称，默认：deepseek-chat",
    )
    args = parser.parse_args()

    diff_path = Path(args.diff_file)
    output_path = Path(args.output)

    if not diff_path.is_file():
        print(f"错误：找不到 Diff 文件：{diff_path}", file=sys.stderr)
        return 1

    try:
        diff_text = diff_path.read_text(encoding="utf-8")

        reviewer = DeepSeekReviewer(model=args.model)
        result, validation = reviewer.review_and_validate(diff_text)

        report = generate_markdown_report(result, validation)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")

    except (OSError, UnicodeError, ReviewError) as exc:
        print(f"执行失败：{exc}", file=sys.stderr)
        return 1

    print("代码审查完成！")
    print(f"模型：{args.model}")
    print(f"模型报告的问题数：{result.finding_count}")
    print(f"通过证据校验：{len(validation.valid_findings)}")
    print(f"未通过证据校验：{len(validation.invalid_findings)}")
    print(f"报告位置：{output_path.resolve()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())