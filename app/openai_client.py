"""
OpenAI client — initializes GPT-5.1 and sends structured review prompts.

Security: API key is read exclusively from the OPENAI_API_KEY environment
variable. It is never logged, returned in responses, or hardcoded.
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy-initialised client — only created on first use so missing keys do not
# crash imports and allow graceful degradation.
# ---------------------------------------------------------------------------
_client = None

MODEL = "gpt-5.1"
TIMEOUT_SECONDS = 60
MAX_COMPLETION_TOKENS = 1500


def _get_client():
    """Return (and lazily create) the OpenAI client."""
    global _client
    if _client is not None:
        return _client

    try:
        from openai import OpenAI  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "openai package is not installed. Add it to requirements.txt."
        ) from exc

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable is not set. "
            "AI review is unavailable."
        )

    _client = OpenAI(api_key=api_key, timeout=TIMEOUT_SECONDS)
    return _client


def send_review_prompt(system_prompt: str, user_prompt: str) -> dict:
    """
    Send a structured prompt to GPT-5.1 and return the parsed JSON response.

    Returns a dict on success.
    Returns a graceful fallback dict on any failure — callers must not raise.
    """
    try:
        client = _get_client()

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_completion_tokens=MAX_COMPLETION_TOKENS,
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        raw_content = response.choices[0].message.content or ""
        return _parse_response(raw_content)

    except RuntimeError as exc:
        logger.warning("AI review skipped: %s", exc)
        return _fallback(str(exc))
    except Exception as exc:  # noqa: BLE001
        logger.error("AI review failed: %s", exc)
        return _fallback("AI review unavailable")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_response(raw: str) -> dict:
    """Parse GPT JSON response; return fallback on malformed output."""
    try:
        data = json.loads(raw)
        # Validate expected keys are present
        required = {
            "ai_summary", "coverage_percentage",
            "missing_requirements", "security_review",
            "architecture_review", "recommendations",
        }
        if not required.issubset(data.keys()):
            logger.warning("GPT response missing expected keys; using partial data.")
        return {
            "ai_summary": str(data.get("ai_summary", "")),
            "coverage_percentage": int(data.get("coverage_percentage", 0)),
            "missing_requirements": list(data.get("missing_requirements", [])),
            "security_review": list(data.get("security_review", [])),
            "architecture_review": list(data.get("architecture_review", [])),
            "recommendations": list(data.get("recommendations", [])),
        }
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        logger.error("Failed to parse GPT response: %s", exc)
        return _fallback("Malformed AI response")


def _fallback(message: str) -> dict:
    """Return a safe fallback payload when AI review cannot complete."""
    return {
        "status": "failed",
        "message": message,
    }
