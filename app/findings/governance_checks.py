"""
Governance checks — flag config file changes, large diffs, and large changesets.
"""

from typing import List

# Filename patterns that indicate configuration files
CONFIG_PATTERNS = [".env", "config", "docker", ".yaml", ".yml"]

# Per-file diff threshold
LARGE_DIFF_THRESHOLD = 100

# Whole-PR thresholds
LARGE_CHANGESET_LINES = 300
LARGE_CHANGESET_FILES = 15


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
    """Flag individual files with more than LARGE_DIFF_THRESHOLD line changes."""
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


def check_large_changeset(files: list) -> List[dict]:
    """Flag the overall PR when total lines or file count exceeds governance thresholds."""
    total_changes = sum(f.get("changes") or 0 for f in files)
    total_files = len(files)

    if total_changes > LARGE_CHANGESET_LINES or total_files > LARGE_CHANGESET_FILES:
        severity = "HIGH" if total_changes > LARGE_CHANGESET_LINES else "MEDIUM"
        findings = [{
            "category": "GOVERNANCE",
            "severity": severity,
            "message": (
                f"Large change set detected "
                f"({total_files} files, {total_changes} total lines) — mandatory senior review"
            ),
            "file": "(entire PR)",
        }]
        return findings
    return []
