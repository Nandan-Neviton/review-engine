"""
Decision engine — balanced AI-assisted governance decision logic.

Combines deterministic rule engine signals with AI review outputs to produce
contextual, explainable governance decisions.

Design principles:
  - Deterministic governance is primary enforcement
  - AI signals refine and balance the decision
  - Sensitive modules increase scrutiny — they do NOT auto-block
  - All decisions are explainable via decision_reason
  - governance_confidence gives a 0-100 quality signal
"""

from typing import Optional

from app.governance_confidence import calculate_governance_confidence

# ---------------------------------------------------------------------------
# Severe security keywords — triggers BLOCKED regardless of other signals
# ---------------------------------------------------------------------------
_SEVERE_KEYWORDS = [
    "hardcoded secret",
    "hardcoded credential",
    "hardcoded key",
    "hardcoded token",
    "exposed secret",
    "exposed credential",
    "auth bypass",
    "authentication bypass",
    "authorization bypass",
    "insecure token",
    "credential exposure",
    "sql injection",
    "command injection",
    "path traversal",
]

# ---------------------------------------------------------------------------
# Coverage thresholds (only applied when a user story was detected)
# ---------------------------------------------------------------------------
_COVERAGE_BLOCKED   = 40   # coverage below this + other signals → BLOCKED
_COVERAGE_APPROVED  = 85   # coverage at or above this → APPROVED candidate
_COVERAGE_SENSITIVE = 80   # sensitive module passes (→ NEEDS_REVIEW) at this level

# ---------------------------------------------------------------------------
# Finding count thresholds
# ---------------------------------------------------------------------------
_HIGH_BLOCK_COUNT = 3   # ≥ this many HIGH quality findings → escalation signal


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def make_decision(
    findings: list,
    ai_review: dict,
    risk_score_label: str,
    user_story_detected: bool = False,
    context_loaded: bool = False,
    files_changed: list = None,
) -> dict:
    """
    Derive a balanced governance decision from deterministic findings + AI review.

    Parameters
    ----------
    findings            Flat list of finding dicts from rule engine.
    ai_review           AI review dict (may be a failure fallback).
    risk_score_label    'LOW' | 'MEDIUM' | 'HIGH' from risk score calculation.
    user_story_detected Whether a user story was identified for this commit.

    Returns
    -------
    {
        "review_decision":      "APPROVED" | "NEEDS_REVIEW" | "BLOCKED",
        "decision_reason":      ["reason 1", ...],
        "governance_confidence": 0-100,
    }
    """
    reasons: list = []
    files = files_changed or []

    # --- Parse AI signals ---
    ai_available = _is_ai_available(ai_review)
    coverage: Optional[int] = ai_review.get("coverage_percentage") if ai_available else None
    ai_security: list = ai_review.get("security_review", []) if ai_available else []
    ai_arch: list = ai_review.get("architecture_review", []) if ai_available else []

    # --- Categorise deterministic findings ---
    high_findings = [f for f in findings if f.get("severity") == "HIGH"]
    medium_findings = [f for f in findings if f.get("severity") == "MEDIUM"]
    sensitive_findings = [
        f for f in findings
        if f.get("category") in ("SECURITY", "SENSITIVE_MODULE")
    ]
    # Quality HIGH findings — excludes pure sensitivity signals
    quality_high = [
        f for f in high_findings
        if f.get("category") not in ("SECURITY", "SENSITIVE_MODULE")
    ]
    has_sensitive_module = len(sensitive_findings) > 0

    # --- Detect severe security issues ---
    severe_from_deterministic = _has_severe_deterministic(findings)
    severe_from_ai = _has_severe_ai_security(ai_security)
    severe_security = severe_from_deterministic or severe_from_ai

    # ================================================================
    # DECISION LOGIC  (evaluated in strict priority order)
    # ================================================================

    # 1. Severe security violation → always BLOCKED
    if severe_security:
        reasons.append("Critical security violation detected")
        if severe_from_ai:
            reasons.append("AI security review identified a severe vulnerability")
        if severe_from_deterministic:
            reasons.append("Deterministic scan flagged a critical security issue")
        decision = "BLOCKED"

    # 2. Critically low user story coverage + multiple HIGH findings → BLOCKED
    elif (
        ai_available
        and user_story_detected
        and coverage is not None
        and coverage < _COVERAGE_BLOCKED
        and len(high_findings) >= 2
    ):
        reasons.append(f"Critically low user story coverage ({coverage}%)")
        reasons.append(f"{len(high_findings)} HIGH governance findings compound the risk")
        decision = "BLOCKED"

    # 3. Many non-sensitive HIGH findings with no AI mitigation → BLOCKED
    elif len(quality_high) >= _HIGH_BLOCK_COUNT and (
        not ai_available
        or (user_story_detected and coverage is not None and coverage < _COVERAGE_BLOCKED)
    ):
        reasons.append(
            f"{len(quality_high)} HIGH severity governance findings require escalation"
        )
        if not ai_available:
            reasons.append("AI review unavailable — conservative deterministic escalation applied")
        decision = "BLOCKED"

    # 4. Sensitive module + strong coverage → NEEDS_REVIEW (not blocked)
    elif (
        has_sensitive_module
        and ai_available
        and user_story_detected
        and coverage is not None
        and coverage >= _COVERAGE_SENSITIVE
    ):
        reasons.append("Sensitive module modified — governance review required")
        reasons.append(f"Strong user story coverage detected ({coverage}%)")
        if high_findings:
            reasons.append(
                f"{len(high_findings)} HIGH finding(s) noted — manual review advised"
            )
        decision = "NEEDS_REVIEW"

    # 5. Sensitive module — any other condition → NEEDS_REVIEW
    elif has_sensitive_module:
        reasons.append("Sensitive module modified — elevated governance scrutiny applied")
        if ai_available and user_story_detected and coverage is not None:
            reasons.append(f"User story coverage at {coverage}% — further validation needed")
        elif ai_available and not user_story_detected:
            reasons.append("No user story reference detected — coverage cannot be assessed")
        else:
            reasons.append("AI review unavailable — conservative escalation applied")
        decision = "NEEDS_REVIEW"

    # 6. High coverage + no HIGH findings + no architecture concerns → APPROVED
    elif (
        ai_available
        and user_story_detected
        and coverage is not None
        and coverage >= _COVERAGE_APPROVED
        and len(high_findings) == 0
        and len(ai_arch) == 0
    ):
        reasons.append(f"Strong user story coverage ({coverage}%)")
        if len(findings) == 0:
            reasons.append("No governance findings detected")
        elif len(findings) <= 2:
            reasons.append("Only minor findings — within governance tolerance")
        if not ai_security:
            reasons.append("No security concerns identified")
        decision = "APPROVED"

    # 7. Moderate risk / partial implementation → NEEDS_REVIEW
    elif risk_score_label == "MEDIUM" or len(medium_findings) > 0:
        reasons.append("Moderate governance findings warrant review")
        if ai_available and user_story_detected and coverage is not None:
            reasons.append(f"User story coverage at {coverage}% — review implementation completeness")
        decision = "NEEDS_REVIEW"

    # 8. Clean commit, no story needed → APPROVED
    elif len(findings) == 0 and risk_score_label == "LOW":
        reasons.append("No governance findings detected")
        if ai_available and coverage is not None and coverage >= 70:
            reasons.append(f"Acceptable user story coverage ({coverage}%)")
        elif not user_story_detected:
            reasons.append("No user story reference — routine change approved")
        decision = "APPROVED"

    # 9. Default conservative fallback
    else:
        reasons.append("Governance review recommended as a precaution")
        if ai_available and coverage is not None:
            reasons.append(f"AI user story coverage: {coverage}%")
        decision = "NEEDS_REVIEW"

    # --- Downgrade APPROVED if architecture concerns exist ---
    if decision == "APPROVED" and len(ai_arch) > 0:
        reasons.append("Architecture observation noted — alignment verification recommended")
        decision = "NEEDS_REVIEW"

    # --- Governance confidence (analysis quality, not implementation quality) ---
    confidence = calculate_governance_confidence(
        ai_review=ai_review,
        context_loaded=context_loaded,
        user_story_detected=user_story_detected,
        files_changed=files,
        findings=findings,
    )

    return {
        "review_decision": decision,
        "decision_reason": reasons,
        "governance_confidence": confidence,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _is_ai_available(ai_review: dict) -> bool:
    """Return True only when the AI review completed successfully."""
    return (
        isinstance(ai_review, dict)
        and ai_review.get("status") != "failed"
        and "coverage_percentage" in ai_review
    )


def _has_severe_deterministic(findings: list) -> bool:
    """Detect severe security issues from deterministic findings alone."""
    # Two or more SECURITY category findings = severe (e.g. auth bypass + exposed token)
    security_count = sum(1 for f in findings if f.get("category") == "SECURITY")
    if security_count >= 2:
        return True
    # Any finding message explicitly mentioning hardcoded secrets
    for f in findings:
        msg = (f.get("message") or "").lower()
        if "hardcoded" in msg or "exposed credential" in msg:
            return True
    return False


def _has_severe_ai_security(ai_security: list) -> bool:
    """Detect severe security signals from AI security_review items."""
    for item in ai_security:
        item_lower = str(item).lower()
        if any(kw in item_lower for kw in _SEVERE_KEYWORDS):
            return True
    return False
