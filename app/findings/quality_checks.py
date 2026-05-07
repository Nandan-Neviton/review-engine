"""
Code quality checks — detect console.log, TODO/FIXME patterns.
"""

from typing import List


def check_console_logs(files: list) -> List[dict]:
    """Flag any file whose patch contains console.log calls."""
    findings = []
    for file in files:
        patch = file.get("patch") or ""
        if "console.log" in patch:
            findings.append({
                "category": "CODE_QUALITY",
                "severity": "LOW",
                "message": "console.log detected — remove before merging",
                "file": file.get("filename", "unknown"),
            })
    return findings


def check_todo_fixme(files: list) -> List[dict]:
    """Flag any file whose patch contains TODO or FIXME comments."""
    findings = []
    for file in files:
        patch = file.get("patch") or ""
        if "TODO" in patch or "FIXME" in patch:
            findings.append({
                "category": "CODE_QUALITY",
                "severity": "LOW",
                "message": "TODO/FIXME found — resolve or track in issue tracker",
                "file": file.get("filename", "unknown"),
            })
    return findings
