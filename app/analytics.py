"""
Analytics engine — computes governance metrics over persisted reviews.
All functions operate on the list returned by storage.get_all_reviews().
"""

from collections import defaultdict
from typing import List


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------

def get_overview(reviews: List[dict]) -> dict:
    """High-level summary across all reviews."""
    repositories = {r.get("repository") for r in reviews}
    developers = {r.get("author") for r in reviews}
    total_findings = sum(len(r.get("findings", [])) for r in reviews)
    high_risk = sum(1 for r in reviews if r.get("risk_score") == "HIGH")

    return {
        "total_reviews": len(reviews),
        "total_repositories": len(repositories),
        "total_developers": len(developers),
        "total_findings": total_findings,
        "high_risk_reviews": high_risk,
    }


# ---------------------------------------------------------------------------
# Developer analytics
# ---------------------------------------------------------------------------

def get_developer_analytics(reviews: List[dict]) -> List[dict]:
    """Per-developer push and risk aggregates."""
    data: dict = defaultdict(lambda: {"pushes": 0, "total_files": 0, "total_risk": 0})

    for r in reviews:
        author = r.get("author") or "unknown"
        data[author]["pushes"] += 1
        data[author]["total_files"] += r.get("total_files_changed", 0)
        data[author]["total_risk"] += r.get("risk_score_value", 0)

    result = []
    for author, stats in data.items():
        pushes = stats["pushes"]
        result.append({
            "author": author,
            "total_pushes": pushes,
            "avg_files_changed": round(stats["total_files"] / pushes, 2),
            "avg_risk_score": round(stats["total_risk"] / pushes, 2),
        })

    return sorted(result, key=lambda x: x["total_pushes"], reverse=True)


# ---------------------------------------------------------------------------
# Repository analytics
# ---------------------------------------------------------------------------

def get_repository_analytics(reviews: List[dict]) -> List[dict]:
    """Per-repository push, risk, and finding aggregates."""
    data: dict = defaultdict(lambda: {"pushes": 0, "total_risk": 0, "total_findings": 0})

    for r in reviews:
        repo = r.get("repository") or "unknown"
        data[repo]["pushes"] += 1
        data[repo]["total_risk"] += r.get("risk_score_value", 0)
        data[repo]["total_findings"] += len(r.get("findings", []))

    result = []
    for repo, stats in data.items():
        result.append({
            "repository": repo,
            "total_pushes": stats["pushes"],
            "total_risk_score": stats["total_risk"],
            "total_findings": stats["total_findings"],
        })

    return sorted(result, key=lambda x: x["total_pushes"], reverse=True)


# ---------------------------------------------------------------------------
# Risk analytics
# ---------------------------------------------------------------------------

def get_risk_analytics(reviews: List[dict]) -> dict:
    """Distribution of risk levels across all reviews."""
    counts: dict = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for r in reviews:
        level = r.get("risk_score", "LOW")
        if level in counts:
            counts[level] += 1
    return counts


# ---------------------------------------------------------------------------
# Recent reviews feed
# ---------------------------------------------------------------------------

def get_recent_reviews(reviews: List[dict], limit: int = 10) -> List[dict]:
    """Return the most recent reviews (newest first), limited to `limit` items."""
    return reviews[:limit]
