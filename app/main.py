from fastapi import FastAPI, Request
import requests
import os
import json

app = FastAPI()


@app.get("/")
async def home():
    return {
        "message": "AI Review Engine Running"
    }


@app.post("/review")
async def review(request: Request):
    payload = await request.json()

    repository = payload["repository"]
    branch = payload["branch"]
    commit_sha = payload["commit_sha"]
    author = payload["author"]

    token = os.getenv("GITHUB_TOKEN")

    github_api_url = f"https://api.github.com/repos/{repository}/commits/{commit_sha}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(github_api_url, headers=headers)

    if response.status_code != 200:
        return {
            "status": "failed",
            "github_status_code": response.status_code,
            "github_response": response.json()
        }

    commit_data = response.json()

    files_changed = []

    for file in commit_data.get("files", []):
        files_changed.append({
            "filename": file.get("filename"),
            "status": file.get("status"),
            "additions": file.get("additions"),
            "deletions": file.get("deletions"),
            "changes": file.get("changes"),
            "patch": file.get("patch")
        })

    review_output = {
        "status": "success",
        "repository": repository,
        "branch": branch,
        "commit_sha": commit_sha,
        "author": author,
        "total_files_changed": len(files_changed),
        "files_changed": files_changed
    }

    print("\n========== REVIEW OUTPUT ==========")
    print(json.dumps(review_output, indent=2))
    print("===================================\n")

    with open("review_output.json", "w") as review_file:
        json.dump(review_output, review_file, indent=2)

    return review_output