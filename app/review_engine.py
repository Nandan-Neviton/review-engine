"""
Review engine — orchestrates a full code review cycle.

Fetches the commit from GitHub, extracts changed files, runs the rule engine,
computes risk score, derives review decision, loads repository context,
and returns a structured record ready for storage and API response.
"""

from datetime import datetime, timezone

from app.github_client import fetch_commit
from app.rule_engine import run_rules, calculate_risk_score
from app.context_loader import load_repo_context
from app.ai_review import run_ai_review
from app.decision_engine import make_decision


def run_review(repository: str, branch: str, commit_sha: str, author: str,
               commit_message: str = "") -> dict:
    """
    Perform a full deterministic review for a given commit.

    Returns a review dict ready for storage and API response.
    Raises RuntimeError if the GitHub API call fails.
    """
    # 1. Fetch commit data from GitHub
    commit_data = fetch_commit(repository, commit_sha)

    # Use the commit message from GitHub if not provided by the caller
    if not commit_message:
        commit_message = (
            commit_data.get("commit", {}).get("message", "") or ""
        )

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

    # 4. Compute risk score (governance sensitivity signal — preserved as-is)
    risk = calculate_risk_score(findings)

    # 5. Load repository context (non-blocking — missing context is fine)
    repo_context_result = load_repo_context(repository, commit_message)
    context_metadata = repo_context_result["metadata"]
    repo_context = repo_context_result["context"]

    # 6. Run AI review (non-blocking — failure falls back gracefully)
    ai_result = run_ai_review(
        context=repo_context,
        detected_user_story=context_metadata["detected_user_story"],
        findings=findings,
        files_changed=files_changed,
        commit_message=commit_message,
    )

    # 7. Derive balanced governance decision (AI-assisted, deterministic primary)
    decision_result = make_decision(
        findings=findings,
        ai_review=ai_result,
        risk_score_label=risk["risk_score"],
        user_story_detected=bool(context_metadata["detected_user_story"]),
    )

    print("\n========== GOVERNANCE DECISION ==========")
    print(f"Decision:   {decision_result['review_decision']}")
    print(f"Confidence: {decision_result['governance_confidence']}%")
    for reason in decision_result["decision_reason"]:
        print(f"  - {reason}")
    print("=========================================\n")

    # 8. Build final review record
    review = {
        "status": "success",
        "repository": repository,
        "branch": branch,
        "commit_sha": commit_sha,
        "author": author,
        "commit_message": commit_message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "risk_score": risk["risk_score"],
        "risk_score_value": risk["risk_score_value"],
        "review_decision": decision_result["review_decision"],
        "decision_reason": decision_result["decision_reason"],
        "governance_confidence": decision_result["governance_confidence"],
        "total_files_changed": len(files_changed),
        "findings": findings,
        "files_changed": files_changed,
        # Lightweight context metadata (no full markdown content exposed)
        "repository_context_loaded": context_metadata["repository_context_loaded"],
        "loaded_context_files": context_metadata["loaded_context_files"],
        "detected_user_story": context_metadata["detected_user_story"],
        "available_user_stories": context_metadata["available_user_stories"],
        # AI governance review (augments deterministic findings)
        "ai_review": ai_result,
    }

    return review
