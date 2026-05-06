from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()


@app.get("/")
async def home():
    return {"message": "AI Review Engine Running"}


@app.post("/review")
async def review(request: Request):
    payload = await request.json()

    repository = payload["repository"]
    commit_sha = payload["commit_sha"]

    token = os.getenv("GITHUB_TOKEN")

    print("\n========== TOKEN DEBUG ==========")
    print("TOKEN EXISTS:", bool(token))
    print("TOKEN LENGTH:", len(token) if token else 0)
    print("TOKEN PREFIX:", token[:6] if token else "NO TOKEN")
    print("=================================\n")

    github_api_url = f"https://api.github.com/repos/{repository}/commits/{commit_sha}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(github_api_url, headers=headers)

    print("\n========== GITHUB API STATUS ==========")
    print("STATUS CODE:", response.status_code)
    print("=======================================\n")

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
        "github_status_code": response.status_code,
        "github_api_response": commit_data,
        "repository": repository,
        "commit_sha": commit_sha,
        "files_changed": files_changed
    }

    print("\n========== REVIEW OUTPUT ==========")
    print(review_output)
    print("===================================\n")

    return review_output