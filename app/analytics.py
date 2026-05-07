"""
Analytics engine — computes governance metrics over persisted reviews.
All functions operate on the list returned by storage.get_all_reviews().
"""

from collections import defaultdict
from datetime import datetime, timezone
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
    blocked = sum(1 for r in reviews if r.get("review_decision") == "BLOCKED")

    return {
        "total_reviews": len(reviews),
        "total_repositories": len(repositories),
        "total_developers": len(developers),
        "total_findings": total_findings,
        "high_risk_reviews": high_risk,
        "blocked_reviews": blocked,
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


# ---------------------------------------------------------------------------
# Engineering health score
# ---------------------------------------------------------------------------

def get_health_score(reviews: List[dict]) -> dict:
    """
    Compute a 0-100 engineering health score from the last 30 reviews.

    Deductions:
      - Each HIGH risk review:    -5
      - Each finding:             -0.5
      - Each SENSITIVE_MODULE finding: -1 extra
      - Each BLOCKED review:      -3
    """
    sample = reviews[:30]
    score = 100.0

    for r in sample:
        risk = r.get("risk_score", "LOW")
        decision = r.get("review_decision", "APPROVED")
        findings = r.get("findings", [])

        if risk == "HIGH":
            score -= 5
        if decision == "BLOCKED":
            score -= 3

        for f in findings:
            score -= 0.5
            if f.get("category") == "SENSITIVE_MODULE":
                score -= 1.0

    score = max(0.0, min(100.0, score))
    rounded = round(score)

    if rounded >= 90:
        label = "EXCELLENT"
    elif rounded >= 75:
        label = "GOOD"
    elif rounded >= 50:
        label = "WARNING"
    else:
        label = "CRITICAL"

    return {"engineering_health_score": rounded, "health_label": label}


# ---------------------------------------------------------------------------
# Hotspot analytics
# ---------------------------------------------------------------------------

def get_hotspots(reviews: List[dict]) -> List[dict]:
    """Track most-modified files and their cumulative risk exposure."""
    file_data: dict = defaultdict(lambda: {"modifications": 0, "risk_score": 0})

    for r in sample_all(reviews):
        risk_val = r.get("risk_score_value", 0)
        for f in r.get("files_changed", []):
            fname = f.get("filename") or "unknown"
            file_data[fname]["modifications"] += 1
            file_data[fname]["risk_score"] += risk_val

    result = [
        {"filename": fname, **stats}
        for fname, stats in file_data.items()
    ]
    return sorted(result, key=lambda x: x["modifications"], reverse=True)


def sample_all(reviews: List[dict]) -> List[dict]:
    """Return all reviews (helper for readability)."""
    return reviews


# ---------------------------------------------------------------------------
# Findings distribution by category
# ---------------------------------------------------------------------------

def get_findings_summary(reviews: List[dict]) -> dict:
    """Count findings grouped by category across all reviews."""
    counts: dict = defaultdict(int)
    for r in reviews:
        for f in r.get("findings", []):
            category = f.get("category", "OTHER")
            counts[category] += 1
    return dict(counts)


# ---------------------------------------------------------------------------
# Activity timeline
# ---------------------------------------------------------------------------

def get_timeline(reviews: List[dict], limit: int = 50) -> List[dict]:
    """
    Generate a chronological activity timeline from review history.
    Returns events newest-first.
    """
    events = []

    for r in reviews:
        ts = r.get("timestamp", "")
        author = r.get("author", "unknown")
        repo = r.get("repository", "unknown")
        risk = r.get("risk_score", "LOW")
        decision = r.get("review_decision", "APPROVED")
        findings = r.get("findings", [])

        # Primary review event
        events.append({
            "timestamp": ts,
            "author": author,
            "repository": repo,
            "event": f"Review submitted — decision: {decision}",
            "type": "REVIEW",
        })

        # High risk event
        if risk == "HIGH":
            events.append({
                "timestamp": ts,
                "author": author,
                "repository": repo,
                "event": "HIGH risk review detected",
                "type": "HIGH_RISK",
            })

        # Sensitive module events (deduplicated per review)
        sensitive_files = [
            f.get("file", "unknown")
            for f in findings
            if f.get("category") == "SENSITIVE_MODULE"
        ]
        if sensitive_files:
            events.append({
                "timestamp": ts,
                "author": author,
                "repository": repo,
                "event": f"Sensitive module modified: {sensitive_files[0]}",
                "type": "SENSITIVE",
            })

    # Already newest-first since reviews are stored that way
    return events[:limit]


# ---------------------------------------------------------------------------
# Text summary
# ---------------------------------------------------------------------------

def get_summary(reviews: List[dict]) -> dict:
    """Generate a human-readable governance summary from recent reviews."""
    if not reviews:
        return {
            "summary": "No reviews processed yet. Push code to a connected repository to begin."
        }

    # Today's reviews
    today = datetime.now(timezone.utc).date()
    today_reviews = [
        r for r in reviews
        if r.get("timestamp", "").startswith(today.isoformat())
    ]

    total = len(reviews)
    blocked = sum(1 for r in reviews if r.get("review_decision") == "BLOCKED")
    high_risk = sum(1 for r in reviews if r.get("risk_score") == "HIGH")

    # Sensitive module frequency
    sensitive_counts: dict = defaultdict(int)
    for r in reviews:
        for f in r.get("findings", []):
            if f.get("category") == "SENSITIVE_MODULE":
                sensitive_counts[f.get("file", "unknown")] += 1

    lines = [
        f"{total} review{'s' if total != 1 else ''} processed in total.",
        f"{len(today_reviews)} review{'s' if len(today_reviews) != 1 else ''} submitted today.",
    ]
    if blocked:
        lines.append(f"{blocked} BLOCKED review{'s' if blocked != 1 else ''} detected.")
    if high_risk:
        lines.append(f"{high_risk} HIGH risk review{'s' if high_risk != 1 else ''} require immediate attention.")
    if sensitive_counts:
        top_file = max(sensitive_counts, key=lambda k: sensitive_counts[k])
        lines.append(
            f"Sensitive module '{top_file}' modified "
            f"{sensitive_counts[top_file]} time{'s' if sensitive_counts[top_file] != 1 else ''}."
        )
    if high_risk > total * 0.3 and total >= 3:
        lines.append("High-risk governance trend observed — engineering review recommended.")

    return {"summary": " ".join(lines)}


# ---------------------------------------------------------------------------
# Decision analytics
# ---------------------------------------------------------------------------

def get_decision_analytics(reviews: List[dict]) -> dict:
    """
    Governance decision distribution and average confidence score.

    Returns counts of APPROVED / NEEDS_REVIEW / BLOCKED decisions alongside
    the average governance_confidence across all reviews that carry the field.
    """
    counts: dict = {"APPROVED": 0, "NEEDS_REVIEW": 0, "BLOCKED": 0}
    confidence_values: list = []

    for r in reviews:
        decision = r.get("review_decision")
        if decision in counts:
            counts[decision] += 1

        confidence = r.get("governance_confidence")
        if isinstance(confidence, (int, float)):
            confidence_values.append(confidence)

    total = sum(counts.values())
    avg_confidence = (
        round(sum(confidence_values) / len(confidence_values))
        if confidence_values
        else None
    )

    return {
        "decisions": counts,
        "total_reviews": total,
        "avg_governance_confidence": avg_confidence,
    }
