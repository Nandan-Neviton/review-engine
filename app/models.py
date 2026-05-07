"""
Data models for the review engine.
Defines shared structures used across storage, analytics, and review modules.
"""

from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class Finding:
    """Represents a single deterministic finding from the rule engine."""
    category: str          # SECURITY | CODE_QUALITY | GOVERNANCE
    severity: str          # LOW | MEDIUM | HIGH
    message: str
    file: str


@dataclass
class FileChanged:
    """Represents a single changed file from a GitHub commit."""
    filename: str
    status: str
    additions: int
    deletions: int
    changes: int
    patch: Optional[str] = None


@dataclass
class ReviewRecord:
    """Represents a full persisted review record."""
    status: str
    repository: str
    branch: str
    commit_sha: str
    author: str
    timestamp: str
    risk_score: str                     # LOW | MEDIUM | HIGH
    risk_score_value: int
    total_files_changed: int
    findings: List[dict] = field(default_factory=list)
    files_changed: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "repository": self.repository,
            "branch": self.branch,
            "commit_sha": self.commit_sha,
            "author": self.author,
            "timestamp": self.timestamp,
            "risk_score": self.risk_score,
            "risk_score_value": self.risk_score_value,
            "total_files_changed": self.total_files_changed,
            "findings": self.findings,
            "files_changed": self.files_changed,
        }
