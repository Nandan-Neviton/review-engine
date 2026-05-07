"""
Rule engine — orchestrates all deterministic checks and computes risk score.
"""

from app.findings.quality_checks import check_console_logs, check_todo_fixme
from app.findings.security_checks import check_auth_files
from app.findings.governance_checks import check_config_changes, check_large_diffs

# Severity → numeric weight mapping
SEVERITY_WEIGHTS = {
    "LOW": 1,
    "MEDIUM": 3,
    "HIGH": 5,
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
    findings.extend(check_config_changes(files))
    findings.extend(check_large_diffs(files))
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
