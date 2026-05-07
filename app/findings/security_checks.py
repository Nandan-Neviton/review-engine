"""
Security checks — flag auth/JWT/middleware/security-related file changes.
"""

from typing import List

# Filename patterns that indicate security-sensitive files
SECURITY_PATTERNS = ["auth", "middleware", "jwt", "security"]


def check_auth_files(files: list) -> List[dict]:
    """Flag changes to authentication or security-related files."""
    findings = []
    for file in files:
        filename = (file.get("filename") or "").lower()
        if any(pattern in filename for pattern in SECURITY_PATTERNS):
            findings.append({
                "category": "SECURITY",
                "severity": "HIGH",
                "message": "Auth-related file modified — requires security review",
                "file": file.get("filename", "unknown"),
            })
    return findings
