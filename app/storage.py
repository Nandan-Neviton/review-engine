"""
Storage layer for the review engine.
Persists all reviews to a local JSON file (reviews.json).
"""

import json
import os

# Path to the persistent reviews file (relative to app/ directory)
REVIEWS_FILE = os.path.join(os.path.dirname(__file__), "reviews.json")


def load_reviews() -> list:
    """Load all reviews from the JSON file. Returns empty list if file missing."""
    if not os.path.exists(REVIEWS_FILE):
        return []
    with open(REVIEWS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return []


def save_review(review: dict) -> None:
    """Append a single review dict to the reviews JSON file."""
    reviews = load_reviews()
    reviews.append(review)
    with open(REVIEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(reviews, f, indent=2)


def get_all_reviews() -> list:
    """Return all persisted reviews, newest first."""
    reviews = load_reviews()
    return list(reversed(reviews))
