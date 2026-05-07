"""
Rule engine — orchestrates all deterministic checks, computes risk score,
and derives the review decision.
"""

from app.findings.quality_checks import check_console_logs, check_todo_fixme
from app.findings.security_checks import check_auth_files, check_sensitive_modules
from app.findings.governance_checks import (
    check_config_changes,
    check_large_diffs,
    check_large_changeset,
)

# Severity → numeric weight mapping
SEVERITY_WEIGHTS = {
    "LOW": 1,
    "MEDIUM": 3,
    "HIGH": 5,
}

# Risk level → review decision
DECISION_MAP = {
    "LOW": "APPROVED",
    "MEDIUM": "NEEDS_REVIEW",
    "HIGH": "BLOCKED",
}


def run_rules(files: list) -> list:
    """
    Run all rule checks against the list of changed files.
    Returns a flat list of finding dicts.
    """
    findings = []
    findings.extend(check_console_logs(files))
    findings.extend(check_todo_fixme(files))
    findings.extend(check_auth_files(files))
    findings.extend(check_sensitive_modules(files))
    findings.extend(check_config_changes(files))
    findings.extend(check_large_diffs(files))
    findings.extend(check_large_changeset(files))
    return findings


def calculate_risk_score(findings: list) -> dict:
    """
    Calculate numeric and string risk score from a list of findings.

    Score bands:
      0-2  => LOW
      3-5  => MEDIUM
      6+   => HIGH
    """
    total = sum(SEVERITY_WEIGHTS.get(f.get("severity", "LOW"), 1) for f in findings)

    if total >= 6:
        label = "HIGH"
    elif total >= 3:
        label = "MEDIUM"
    else:
        label = "LOW"

    return {"risk_score_value": total, "risk_score": label}


def get_review_decision(risk_score: str) -> str:
    """Derive deterministic review decision from risk level."""
    return DECISION_MAP.get(risk_score, "NEEDS_REVIEW")
