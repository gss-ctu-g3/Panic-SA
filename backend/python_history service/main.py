from fastapi import FastAPI
from routes.history import router
from typing import Any

app = FastAPI(title="History API", version="1.0.0")

@app.get("/")
def root() -> Any:
    return {"message": "History API is running"}

app.include_router(
    router,
    prefix="/api/v1/history",
    tags=["History API"]
)
