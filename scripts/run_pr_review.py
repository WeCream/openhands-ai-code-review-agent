import json
import os
import sys
import urllib.request
from dataclasses import asdict
from pathlib import Path

# Add project root to Python import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.reviewer import DeepSeekReviewer

def get_pr_diff() -> str:
    repository = os.environ["GITHUB_REPOSITORY"]
    pr_number = os.environ["PR_NUMBER"]
    github_token = os.environ["GITHUB_TOKEN"]

    url = (
        f"https://api.github.com/repos/{repository}"
        f"/pulls/{pr_number}"
    )

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


if __name__ == "__main__":
    main()
