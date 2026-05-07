"""
Security checks — flag auth/JWT/middleware/security/payment-related file changes.
"""

from typing import List

# Filename patterns that indicate security-sensitive files
SECURITY_PATTERNS = ["auth", "middleware", "jwt", "security"]

# Sensitive module keywords covering a broader governance scope
SENSITIVE_MODULE_PATTERNS = [
    "auth", "middleware", "security", "jwt",
    "database", "payment", "config", "docker",
    "yaml", "github/workflows",
]


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


def check_sensitive_modules(files: list) -> List[dict]:
    """Flag changes to sensitive modules (payment, DB, CI pipelines, etc.)."""
    findings = []
    for file in files:
        filename = (file.get("filename") or "").lower()
        if any(pattern in filename for pattern in SENSITIVE_MODULE_PATTERNS):
            findings.append({
                "category": "SENSITIVE_MODULE",
                "severity": "HIGH",
                "message": f"Sensitive module modified — escalated governance review required",
                "file": file.get("filename", "unknown"),
            })
    return findings
