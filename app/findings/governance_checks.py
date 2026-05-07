"""
Governance checks — flag config file changes and large diffs.
"""

from typing import List

# Filename patterns that indicate configuration files
CONFIG_PATTERNS = [".env", "config", "docker", ".yaml", ".yml"]

# Threshold for flagging a file as a large diff
LARGE_DIFF_THRESHOLD = 100


def check_config_changes(files: list) -> List[dict]:
    """Flag changes to environment or configuration files."""
    findings = []
    for file in files:
        filename = (file.get("filename") or "").lower()
        if any(pattern in filename for pattern in CONFIG_PATTERNS):
            findings.append({
                "category": "GOVERNANCE",
                "severity": "MEDIUM",
                "message": "Config/environment file modified — review carefully",
                "file": file.get("filename", "unknown"),
            })
    return findings


def check_large_diffs(files: list) -> List[dict]:
    """Flag files with more than LARGE_DIFF_THRESHOLD total line changes."""
    findings = []
    for file in files:
        changes = file.get("changes") or 0
        if changes > LARGE_DIFF_THRESHOLD:
            findings.append({
                "category": "GOVERNANCE",
                "severity": "MEDIUM",
                "message": f"Large diff detected ({changes} lines changed) — consider splitting the PR",
                "file": file.get("filename", "unknown"),
            })
    return findings
