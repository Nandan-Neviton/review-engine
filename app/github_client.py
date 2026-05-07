"""
GitHub API client — handles all communication with the GitHub REST API.
"""

import os
import base64
import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# Maximum file line count beyond which full content is not fetched (cost control)
_FULL_FILE_LINE_THRESHOLD = 300


def fetch_commit(repository: str, commit_sha: str) -> dict:
    """
    Fetch full commit details from GitHub.

    Returns the parsed JSON response on success, or raises a RuntimeError
    with the HTTP status code and GitHub error body on failure.
    """
    token = os.getenv("GITHUB_TOKEN")
    url = f"https://api.github.com/repos/{repository}/commits/{commit_sha}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    response = requests.get(url, headers=headers, timeout=15)

    if response.status_code != 200:
        raise RuntimeError(
            f"GitHub API error {response.status_code}: {response.text}"
        )

    return response.json()


def fetch_file_content(repository: str, file_path: str, ref: str) -> Optional[str]:
    """
    Fetch the decoded text content of a single file at a specific ref (commit SHA or branch).

    Returns the file content as a string, or None if:
    - the file does not exist at that ref
    - the file is binary
    - the file exceeds the line threshold
    - the API call fails

    Never raises — all failures return None so the caller degrades gracefully.
    """
    token = os.getenv("GITHUB_TOKEN")
    url = f"https://api.github.com/repos/{repository}/contents/{file_path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    params = {"ref": ref}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
    except requests.RequestException as exc:
        logger.warning("Failed to fetch file content for %s@%s: %s", file_path, ref, exc)
        return None

    if response.status_code != 200:
        return None

    data = response.json()
    encoding = data.get("encoding", "")
    content_b64 = data.get("content", "")

    if encoding != "base64" or not content_b64:
        return None

    try:
        decoded = base64.b64decode(content_b64).decode("utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        return None

    # Skip large files — they exceed our prompt budget
    line_count = decoded.count("\n")
    if line_count > _FULL_FILE_LINE_THRESHOLD:
        logger.debug("Skipping full content for %s (%d lines > threshold)", file_path, line_count)
        return None

    return decoded
