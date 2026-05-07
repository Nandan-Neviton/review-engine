"""
Context loader — automatically loads repository-specific governance context
from markdown files stored under repo-contexts/<repo-name>/.

Designed to be AI-ready: future integrations can pass the returned context
object directly into an LLM prompt builder.
"""

import os
import re
from typing import Optional

# Root of context folders, relative to the project root (one level above app/)
_CONTEXTS_ROOT = os.path.join(os.path.dirname(__file__), "..", "repo-contexts")

# Standard context files to load (filename → context key)
CONTEXT_FILES = {
    "architecture.md":       "architecture",
    "business-context.md":   "business_context",
    "coding-rules.md":       "coding_rules",
    "review-guidelines.md":  "review_guidelines",
    "repo-summary.md":       "repo_summary",
}

# Regex to extract user story IDs from commit messages or PR titles
# Matches patterns like [US-101], US-101, #US-101
_US_PATTERN = re.compile(r"\bUS-\d+\b", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_repo_name(full_repository: str) -> str:
    """
    Extract the bare repository name from a full GitHub path.

    Example: 'Nandan-Neviton/sample-app-for-review' → 'sample-app-for-review'
    """
    return full_repository.split("/")[-1]


def load_repo_context(repository: str, commit_message: str = "") -> dict:
    """
    Load all available context for *repository* and return a structured dict.

    Parameters
    ----------
    repository      Full GitHub repository path (e.g. 'org/repo-name').
    commit_message  Optional commit message used for user-story detection.

    Returns
    -------
    Structured context dict — safe to attach to review output or pass to AI.
    """
    repo_name = extract_repo_name(repository)
    context_dir = os.path.normpath(os.path.join(_CONTEXTS_ROOT, repo_name))

    # --- Load standard markdown files ---
    loaded_files: list[str] = []
    context: dict = {
        "repository_name": repo_name,
        "architecture":      None,
        "business_context":  None,
        "coding_rules":      None,
        "review_guidelines": None,
        "repo_summary":      None,
        "user_stories":      {},
    }

    if os.path.isdir(context_dir):
        for filename, key in CONTEXT_FILES.items():
            filepath = os.path.join(context_dir, filename)
            content = _safe_read(filepath)
            if content is not None:
                context[key] = content
                loaded_files.append(filename)

        # --- Load user stories ---
        stories_dir = os.path.join(context_dir, "user-stories")
        if os.path.isdir(stories_dir):
            for fname in sorted(os.listdir(stories_dir)):
                if fname.lower().endswith(".md"):
                    story_id = os.path.splitext(fname)[0].upper()
                    content = _safe_read(os.path.join(stories_dir, fname))
                    if content is not None:
                        context["user_stories"][story_id] = content

    # --- Detect user story reference in commit message ---
    detected_story = _detect_user_story(commit_message, context["user_stories"])

    # --- Consolidated log block ---
    print("\n========== CONTEXT LOADER ==========")
    print(f"Repository detected:  {repo_name}")
    print(f"Context folder:       {context_dir}")
    if loaded_files:
        for fname in loaded_files:
            print(f"Loaded:               {fname}")
        for story_id in context["user_stories"]:
            print(f"Loaded user story:    {story_id}")
    else:
        print("No context files found — skipping.")
    if detected_story:
        print(f"Detected user story:  {detected_story}")
    print("====================================\n")

    return _build_result(context, loaded_files, detected_story)


# ---------------------------------------------------------------------------
# Context-status analytics
# ---------------------------------------------------------------------------

def get_context_status(reviews: list) -> dict:
    """
    Return an overview of which repositories have context available.

    Walks repo-contexts/ and compares against reviewed repositories.
    Also surfaces the most recently detected user story.
    """
    contexts_root = os.path.normpath(_CONTEXTS_ROOT)

    # Repos that have a context folder
    repos_with_context: set[str] = set()
    total_user_stories = 0

    if os.path.isdir(contexts_root):
        for entry in os.scandir(contexts_root):
            if entry.is_dir():
                repos_with_context.add(entry.name)
                stories_dir = os.path.join(entry.path, "user-stories")
                if os.path.isdir(stories_dir):
                    total_user_stories += sum(
                        1 for f in os.scandir(stories_dir) if f.name.endswith(".md")
                    )

    # Repos seen in review history but without a context folder
    reviewed_repos = {
        extract_repo_name(r.get("repository", ""))
        for r in reviews
        if r.get("repository")
    }
    missing = reviewed_repos - repos_with_context

    # Latest detected user story across all reviews (newest-first order)
    latest_detected_story = None
    for r in reviews:
        story = r.get("detected_user_story")
        if story:
            latest_detected_story = story
            break

    return {
        "repositories_with_context": len(repos_with_context),
        "repositories_missing_context": len(missing),
        "loaded_user_stories": total_user_stories,
        "latest_detected_story": latest_detected_story,
        "repos_with_context": sorted(repos_with_context),
        "repos_missing_context": sorted(missing),
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _safe_read(filepath: str) -> Optional[str]:
    """Read a file and return its contents, or None if it doesn't exist."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read().strip()
    except (OSError, IOError):
        return None


def _detect_user_story(commit_message: str, available_stories: dict) -> Optional[str]:
    """Return the first user-story ID found in commit_message, if it exists in context."""
    if not commit_message:
        return None
    matches = _US_PATTERN.findall(commit_message)
    for match in matches:
        story_id = match.upper()
        if story_id in available_stories:
            return story_id
    # Return first match even if not in stories (may still be useful)
    return matches[0].upper() if matches else None


def _build_result(context: dict, loaded_files: list, detected_story: Optional[str]) -> dict:
    """Wrap context + loader metadata into a single result object."""
    return {
        # Full content (kept internal — do not expose wholesale in API responses)
        "context": context,
        # Lightweight metadata (safe to attach to review API responses)
        "metadata": {
            "repository_name":          context["repository_name"],
            "repository_context_loaded": len(loaded_files) > 0,
            "loaded_context_files":      loaded_files,
            "available_user_stories":    list(context["user_stories"].keys()),
            "detected_user_story":       detected_story,
        },
    }
