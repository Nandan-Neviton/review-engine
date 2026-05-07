"""
Prompt builder — constructs structured prompts for GPT-5.1 governance review.

Design goals:
- Keep prompts concise; never dump entire repositories.
- Combine only the data that is directly relevant to this review.
- Cap all text sections to safe token limits.
"""

from typing import Optional

# ---------------------------------------------------------------------------
# Character limits for each context section (MVP cost control)
# ---------------------------------------------------------------------------
_MAX_CODING_RULES      = 1500
_MAX_GUIDELINES        = 1000
_MAX_ARCHITECTURE      = 1000
_MAX_BUSINESS_CONTEXT  = 800
_MAX_USER_STORY        = 1200
_MAX_DIFF_PER_FILE     = 600
_MAX_DIFF_FILES        = 5
_MAX_FINDINGS_CHARS    = 800

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an Enterprise Engineering Governance Reviewer.

Your role is to perform a structured, context-aware code review based on:
- Repository governance rules and coding standards
- User story requirements and acceptance criteria
- Deterministic rule engine findings already detected
- Code changes (diffs) introduced in this commit

You must respond with ONLY a valid JSON object — no markdown, no prose outside JSON.

Required JSON structure:
{
  "ai_summary": "Concise description of what this change does and its governance impact",
  "coverage_percentage": <integer 0-100>,
  "missing_requirements": ["requirement not addressed", ...],
  "security_review": ["security observation", ...],
  "architecture_review": ["architecture observation", ...],
  "recommendations": ["actionable recommendation", ...]
}

Rules:
- coverage_percentage reflects how well the code change addresses the user story (0 if no story detected)
- Keep all lists concise — maximum 5 items each
- Be specific and actionable
- Do not repeat findings already listed verbatim; synthesize them"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_review_prompt(
    context: dict,
    detected_user_story: Optional[str],
    findings: list,
    files_changed: list,
    commit_message: str = "",
) -> str:
    """
    Build the user-turn prompt for GPT-5.1 review.

    Parameters
    ----------
    context           Full context dict from context_loader (contains coding_rules, etc.)
    detected_user_story  Story ID string (e.g. 'US-101') or None
    findings          List of deterministic finding dicts from rule engine
    files_changed     List of changed file dicts (including patches)
    commit_message    The commit message for this push
    """
    sections: list[str] = []

    # --- Commit message ---
    if commit_message:
        sections.append(f"## Commit Message\n{commit_message.strip()}")

    # --- Repository summary ---
    repo_summary = context.get("repo_summary")
    if repo_summary:
        sections.append(f"## Repository Summary\n{_truncate(repo_summary, 600)}")

    # --- Business context ---
    business_context = context.get("business_context")
    if business_context:
        sections.append(
            f"## Business Context\n{_truncate(business_context, _MAX_BUSINESS_CONTEXT)}"
        )

    # --- Architecture ---
    architecture = context.get("architecture")
    if architecture:
        sections.append(
            f"## Architecture Overview\n{_truncate(architecture, _MAX_ARCHITECTURE)}"
        )

    # --- Coding rules ---
    coding_rules = context.get("coding_rules")
    if coding_rules:
        sections.append(
            f"## Coding Rules & Standards\n{_truncate(coding_rules, _MAX_CODING_RULES)}"
        )

    # --- Review guidelines ---
    review_guidelines = context.get("review_guidelines")
    if review_guidelines:
        sections.append(
            f"## Review Guidelines\n{_truncate(review_guidelines, _MAX_GUIDELINES)}"
        )

    # --- User story ---
    if detected_user_story:
        user_stories = context.get("user_stories", {})
        story_content = user_stories.get(detected_user_story)
        if story_content:
            sections.append(
                f"## User Story: {detected_user_story}\n"
                f"{_truncate(story_content, _MAX_USER_STORY)}"
            )
        else:
            sections.append(f"## Detected User Story Reference\n{detected_user_story}")
    else:
        sections.append(
            "## User Story\nNo user story reference detected in commit message. "
            "Set coverage_percentage to 0."
        )

    # --- Deterministic findings ---
    if findings:
        findings_text = _format_findings(findings)
        sections.append(
            f"## Governance Rule Engine Findings\n"
            f"{_truncate(findings_text, _MAX_FINDINGS_CHARS)}"
        )
    else:
        sections.append("## Governance Rule Engine Findings\nNo findings detected.")

    # --- Changed files with diffs ---
    diff_section = _format_diffs(files_changed)
    if diff_section:
        sections.append(f"## Code Changes\n{diff_section}")

    sections.append(
        "## Task\nReview the above commit against the governance rules, "
        "user story requirements, and architecture. "
        "Respond with the required JSON only."
    )

    return "\n\n".join(sections)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _truncate(text: str, max_chars: int) -> str:
    """Truncate text to max_chars, appending an ellipsis indicator."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n... [truncated]"


def _format_findings(findings: list) -> str:
    lines = []
    for f in findings:
        severity = f.get("severity", "")
        message = f.get("message", "")
        filename = f.get("file", "")
        category = f.get("category", "")
        lines.append(f"- [{severity}] {category}: {message} ({filename})")
    return "\n".join(lines)


def _format_diffs(files_changed: list) -> str:
    """Format diffs for the prompt; cap total files and diff size."""
    parts = []
    for file in files_changed[:_MAX_DIFF_FILES]:
        filename = file.get("filename", "unknown")
        patch = file.get("patch") or ""
        additions = file.get("additions", 0)
        deletions = file.get("deletions", 0)

        header = f"### {filename} (+{additions} / -{deletions})"
        if patch:
            diff_text = _truncate(patch, _MAX_DIFF_PER_FILE)
            parts.append(f"{header}\n```diff\n{diff_text}\n```")
        else:
            parts.append(f"{header}\n(binary or no patch available)")

    if len(files_changed) > _MAX_DIFF_FILES:
        omitted = len(files_changed) - _MAX_DIFF_FILES
        parts.append(f"... and {omitted} more file(s) omitted for brevity.")

    return "\n\n".join(parts)
