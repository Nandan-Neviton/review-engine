import json

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.review_engine import run_review
from app.storage import save_review, get_all_reviews
from app import analytics
from app.context_loader import get_context_status

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Latest review cached in memory for fast access by the frontend
LATEST_REVIEW: dict = {}


# ---------------------------------------------------------------------------
# Core endpoints (preserved)
# ---------------------------------------------------------------------------

@app.get("/")
async def home():
    return {"message": "AI Review Engine Running"}


@app.get("/latest-review")
async def latest_review():
    """Return the most recently processed review (in-memory cache)."""
    return LATEST_REVIEW


@app.post("/review")
async def review(request: Request):
    """
    Trigger a full deterministic code review for a GitHub commit.
    Persists the result to reviews.json and updates the in-memory cache.
    """
    global LATEST_REVIEW

    payload = await request.json()

    repository = payload["repository"]
    branch = payload["branch"]
    commit_sha = payload["commit_sha"]
    author = payload["author"]
    # Optional: GitHub Actions can pass the commit message for user-story detection
    commit_message = payload.get("commit_message", "")

    try:
        review_output = run_review(repository, branch, commit_sha, author, commit_message)
    except RuntimeError as exc:
        return {"status": "failed", "error": str(exc)}

    # Persist to JSON storage
    save_review(review_output)

    # Update in-memory latest review
    LATEST_REVIEW = review_output

    print("\n========== REVIEW OUTPUT ==========")
    print(json.dumps(review_output, indent=2))
    print("===================================\n")

    return review_output


# ---------------------------------------------------------------------------
# Review history endpoint
# ---------------------------------------------------------------------------

@app.get("/reviews")
async def all_reviews():
    """Return all persisted reviews, newest first."""
    return get_all_reviews()


# ---------------------------------------------------------------------------
# Analytics endpoints
# ---------------------------------------------------------------------------

@app.get("/analytics/overview")
async def analytics_overview():
    """High-level governance summary across all reviews."""
    reviews = get_all_reviews()
    return analytics.get_overview(reviews)


@app.get("/analytics/developers")
async def analytics_developers():
    """Per-developer push and risk metrics."""
    reviews = get_all_reviews()
    return analytics.get_developer_analytics(reviews)


@app.get("/analytics/repositories")
async def analytics_repositories():
    """Per-repository push, risk, and finding aggregates."""
    reviews = get_all_reviews()
    return analytics.get_repository_analytics(reviews)


@app.get("/analytics/risks")
async def analytics_risks():
    """Distribution of LOW / MEDIUM / HIGH risk reviews."""
    reviews = get_all_reviews()
    return analytics.get_risk_analytics(reviews)


# ---------------------------------------------------------------------------
# New governance analytics endpoints
# ---------------------------------------------------------------------------

@app.get("/analytics/health")
async def analytics_health():
    """Engineering health score (0-100) with label."""
    reviews = get_all_reviews()
    return analytics.get_health_score(reviews)


@app.get("/analytics/hotspots")
async def analytics_hotspots():
    """Most-modified files ranked by modification count and cumulative risk."""
    reviews = get_all_reviews()
    return analytics.get_hotspots(reviews)


@app.get("/analytics/findings-summary")
async def analytics_findings_summary():
    """Findings count grouped by category across all reviews."""
    reviews = get_all_reviews()
    return analytics.get_findings_summary(reviews)


@app.get("/analytics/timeline")
async def analytics_timeline():
    """Chronological activity timeline, newest first."""
    reviews = get_all_reviews()
    return analytics.get_timeline(reviews)


@app.get("/analytics/summary")
async def analytics_summary():
    """Human-readable governance summary generated from review history."""
    reviews = get_all_reviews()
    return analytics.get_summary(reviews)


@app.get("/analytics/decisions")
async def analytics_decisions():
    """Governance decision distribution (APPROVED / NEEDS_REVIEW / BLOCKED) and avg confidence."""
    reviews = get_all_reviews()
    return analytics.get_decision_analytics(reviews)


@app.get("/analytics/context-status")
async def analytics_context_status():
    """Overview of which repositories have governance context files loaded."""
    reviews = get_all_reviews()
    return get_context_status(reviews)