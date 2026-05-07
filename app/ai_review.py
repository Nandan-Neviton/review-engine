"""
AI review orchestrator — combines prompt builder and OpenAI client to produce
a structured AI governance review that augments (not replaces) deterministic
rule-engine findings.
"""

import logging
from typing import Optional

from app.prompt_builder import SYSTEM_PROMPT, build_review_prompt
from app.openai_client import send_review_prompt

logger = logging.getLogger(__name__)


def run_ai_review(
    context: dict,
    detected_user_story: Optional[str],
    findings: list,
    files_changed: list,
    commit_message: str = "",
) -> dict:
    """
    Orchestrate a full AI governance review for a single commit.

    This function is designed to NEVER raise — if anything goes wrong the
    deterministic pipeline continues unaffected and a graceful fallback is
    attached to the review output.

    Parameters
    ----------
    context             Full context dict from context_loader.
    detected_user_story Story ID (e.g. 'US-101') or None.
    findings            Deterministic findings list from rule engine.
    files_changed       List of changed file dicts with patch data.
    commit_message      Commit message string.

    Returns
    -------
    AI review dict — either a full result or a fallback with status='failed'.
    """
    print("\n========== AI REVIEW ==========")
    print("GPT-5.1 review started")

    repo_name = context.get("repository_name", "unknown")
    print(f"Repository context loaded: {repo_name}")

    if detected_user_story:
        print(f"User story: {detected_user_story}")
    else:
        print("User story: not detected")

    try:
        user_prompt = build_review_prompt(
            context=context,
            detected_user_story=detected_user_story,
            findings=findings,
            files_changed=files_changed,
            commit_message=commit_message,
        )

        result = send_review_prompt(SYSTEM_PROMPT, user_prompt)
        print("AI coverage analysis completed")
        print("================================\n")
        return result

    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error in AI review orchestration: %s", exc)
        print("AI review failed — deterministic pipeline unaffected")
        print("================================\n")
        return {
            "status": "failed",
            "message": "AI review unavailable",
        }
