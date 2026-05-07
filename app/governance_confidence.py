"""
Governance confidence engine — measures certainty and quality of the review analysis.

KEY DISTINCTION:
  Confidence = how certain we are the governance review is thorough and complete.
  It is NOT a measure of implementation quality or finding severity.

A review with severe findings AND detailed AI analysis → HIGH confidence (85-95%).
  We are confident in the findings and confident in the decision.

A review with missing context and no AI → LOW confidence (20-40%).
  We lack the information needed to make a well-grounded decision.

This score is displayed on the dashboard as "Review Quality" or "Analysis Confidence",
making governance decisions explainable and trustworthy.
"""

# ---------------------------------------------------------------------------
# Scoring constants
# ---------------------------------------------------------------------------

_BASE_SCORE = 30

# Positive signals — confidence increases when analysis is more thorough
_AI_COMPLETED            = 25   # AI review ran successfully (biggest signal)
_CONTEXT_LOADED          = 10   # Repository context files were found and loaded
_USER_STORY_DETECTED     = 10   # A user story was matched in the commit message
_MULTI_FILE_ANALYSIS     = 5    # More than one file was analyzed
_AI_SECURITY_POPULATED   = 5    # AI security_review section has content
_AI_ARCH_POPULATED       = 5    # AI architecture_review section has content
_AI_RECOMMENDATIONS      = 5    # AI provided recommendations
_AI_SUMMARY_SUBSTANTIAL  = 5    # AI summary is detailed (> 50 chars)
_FINDINGS_ALIGNMENT      = 5    # Both AI and deterministic found issues (cross-validation)

# Negative signals — confidence decreases when analysis is incomplete
_NO_CONTEXT              = -5   # No repository context available
_NO_USER_STORY           = -5   # No user story detected (coverage cannot be assessed)
_DIFFS_TRUNCATED         = -5   # Diffs were truncated, reducing analysis depth

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def calculate_governance_confidence(
    ai_review: dict,
    context_loaded: bool,
    user_story_detected: bool,
    files_changed: list,
    findings: list,
) -> int:
    """
    Compute a 0-100 governance confidence score.

    Parameters
    ----------
    ai_review           AI review dict (may be a failure fallback).
    context_loaded      Whether repository context files were successfully loaded.
    user_story_detected Whether a user story was identified for this commit.
    files_changed       List of changed file dicts (used for multi-file and truncation checks).
    findings            Deterministic findings from rule engine.

    Returns
    -------
    Integer 0-100 representing confidence in the governance analysis quality.
    """
    score = float(_BASE_SCORE)

    ai_available = _is_ai_available(ai_review)

    # --- AI review quality signals ---
    if ai_available:
        score += _AI_COMPLETED

        ai_summary = ai_review.get("ai_summary", "")
        if len(str(ai_summary)) > 50:
            score += _AI_SUMMARY_SUBSTANTIAL

        if ai_review.get("security_review"):
            score += _AI_SECURITY_POPULATED

        if ai_review.get("architecture_review"):
            score += _AI_ARCH_POPULATED

        if ai_review.get("recommendations"):
            score += _AI_RECOMMENDATIONS

        # Cross-validation: both AI and deterministic flagged issues independently
        has_deterministic_findings = len(findings) > 0
        has_ai_security_findings = len(ai_review.get("security_review", [])) > 0
        if has_deterministic_findings and has_ai_security_findings:
            score += _FINDINGS_ALIGNMENT

    # --- Context quality signals ---
    if context_loaded:
        score += _CONTEXT_LOADED
    else:
        score += _NO_CONTEXT

    if user_story_detected:
        score += _USER_STORY_DETECTED
    else:
        score += _NO_USER_STORY

    # --- File analysis depth signals ---
    if len(files_changed) > 1:
        score += _MULTI_FILE_ANALYSIS

    # Truncated diffs reduce confidence in AI's ability to fully assess the change
    truncated_count = sum(
        1 for f in files_changed
        if "[truncated]" in (f.get("patch") or "")
    )
    if truncated_count > 0:
        score += _DIFFS_TRUNCATED

    return max(0, min(100, round(score)))


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _is_ai_available(ai_review: dict) -> bool:
    """Return True only when the AI review completed successfully."""
    return (
        isinstance(ai_review, dict)
        and ai_review.get("status") != "failed"
        and "coverage_percentage" in ai_review
    )
