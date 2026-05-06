from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/")
async def home():
    return {"message": "AI Review Engine Running"}


@app.post("/review")
async def review(request: Request):
    payload = await request.json()

    print("\n===== REVIEW REQUEST RECEIVED =====")
    print(payload)
    print("===================================\n")

    return {
        "status": "success",
        "message": "Review payload received",
        "received_data": payload
    }