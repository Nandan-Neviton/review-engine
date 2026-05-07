"""
GitHub API client — handles all communication with the GitHub REST API.
"""

import os
import requests


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
