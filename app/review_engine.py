"""
Review engine — orchestrates a full code review cycle.

Fetches the commit from GitHub, extracts changed files, runs the rule engine,
computes risk score, derives review decision, and returns a structured record.
"""

from datetime import datetime, timezone

from app.github_client import fetch_commit
from app.rule_engine import run_rules, calculate_risk_score, get_review_decision


def run_review(repository: str, branch: str, commit_sha: str, author: str) -> dict:
    """
    Perform a full deterministic review for a given commit.

    Returns a review dict ready for storage and API response.
    Raises RuntimeError if the GitHub API call fails.
    """
    # 1. Fetch commit data from GitHub
    commit_data = fetch_commit(repository, commit_sha)

    # 2. Extract changed files
    files_changed = []
    for file in commit_data.get("files", []):
        files_changed.append({
            "filename": file.get("filename"),
            "status": file.get("status"),
            "additions": file.get("additions", 0),
            "deletions": file.get("deletions", 0),
            "changes": file.get("changes", 0),
            "patch": file.get("patch"),
        })

    # 3. Run deterministic rule engine
    findings = run_rules(files_changed)

    # 4. Compute risk score
    risk = calculate_risk_score(findings)

    # 5. Derive review decision
    decision = get_review_decision(risk["risk_score"])

    # 6. Build final review record
    review = {
        "status": "success",
        "repository": repository,
        "branch": branch,
        "commit_sha": commit_sha,
        "author": author,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "risk_score": risk["risk_score"],
        "risk_score_value": risk["risk_score_value"],
        "review_decision": decision,
        "total_files_changed": len(files_changed),
        "findings": findings,
        "files_changed": files_changed,
    }

    return review
