from fastapi import FastAPI, Request
import requests

app = FastAPI()


@app.get("/")
async def home():
    return {"message": "AI Review Engine Running"}


@app.post("/review")
async def review(request: Request):
    payload = await request.json()

    repository = payload["repository"]
    commit_sha = payload["commit_sha"]

    github_api_url = f"https://api.github.com/repos/{repository}/commits/{commit_sha}"

    response = requests.get(github_api_url)

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
        "repository": repository,
        "commit_sha": commit_sha,
        "files_changed": files_changed
    }

    print("\n===== REVIEW OUTPUT =====")
    print(review_output)
    print("=========================\n")

    return review_output