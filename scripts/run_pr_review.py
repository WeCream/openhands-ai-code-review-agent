
import json
import os
import sys
import urllib.request
import urllib.error
from dataclasses import asdict
from pathlib import Path

# Add project root to Python import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.reviewer import DeepSeekReviewer


def get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Required environment variable is missing: {name}")
    return value


def get_pr_diff() -> str:
    repository = get_required_env("GITHUB_REPOSITORY")
    pr_number = get_required_env("PR_NUMBER")
    github_token = get_required_env("GITHUB_TOKEN")

    url = f"https://api.github.com/repos/{repository}/pulls/{pr_number}"

    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3.diff",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def build_review_comment(result) -> str:
    lines = [
        "## AI Code Review Report",
        "",
        f"**Summary:** {result.summary}",
        "",
    ]

    if not result.findings:
        lines.extend([
            "### Findings",
            "",
            "No issues were identified by the AI reviewer.",
        ])
        return "\n".join(lines)

    lines.extend([
        f"### Findings ({len(result.findings)})",
        "",
    ])

    for index, finding in enumerate(result.findings, start=1):
        lines.extend([
            f"#### {index}. [{finding.severity.upper()}] {finding.title}",
            "",
            f"- **File:** `{finding.file_path}`",
            f"- **Line:** {finding.line}",
            f"- **Issue type:** `{finding.issue_type}`",
            f"- **Description:** {finding.description}",
            f"- **Evidence:**",
            "```text",
            finding.evidence,
            "```",
            f"- **Suggestion:** {finding.suggestion}",
            "",
        ])

    lines.extend([
        "---",
        "_Generated automatically by OpenHands AI Application Code Review Agent._",
    ])

    return "\n".join(lines)


def post_pr_review(comment_body: str) -> None:
    repository = get_required_env("GITHUB_REPOSITORY")
    pr_number = get_required_env("PR_NUMBER")
    github_token = get_required_env("GITHUB_TOKEN")

    url = (
        f"https://api.github.com/repos/{repository}"
        f"/pulls/{pr_number}/reviews"
    )

    payload = {
        "body": comment_body,
        "event": "COMMENT",
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            print(f"PR review published successfully. Review ID: {result.get('id')}")
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API rejected the review: HTTP {error.code}: {details}"
        ) from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Unable to reach GitHub API: {error}") from error


def main() -> None:
    diff_text = get_pr_diff()

    if not diff_text.strip():
        raise RuntimeError("PR diff is empty")

    reviewer = DeepSeekReviewer()
    result, validation = reviewer.review_and_validate(diff_text)

    output = {
        "summary": result.summary,
        "findings": [asdict(item) for item in result.findings],
        "validation": str(validation),
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))

    comment_body = build_review_comment(result)
    post_pr_review(comment_body)


if __name__ == "__main__":
    main()
