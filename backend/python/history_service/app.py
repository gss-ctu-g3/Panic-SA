import os
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pymongo import MongoClient

from schemas import AlertResponse, UserAlertsResponse


#our custom lifespan as the docs say for db
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[PANICSA-API-HISTORY] | Started")
    mongo_uri = ENV_MONGO_URI
    client: MongoClient[Dict[str, Any]] | None = None
    db: Any | None = None

    try:
        #init the db cleint
        client = MongoClient(mongo_uri)

        #set the client to app state
        app.state.mongo_client = client
        #db is panic_sa for alerts btw
        db = client["panic_sa"]
        #set the db
        app.state.db = db

        #index for listing alerts by user
        db["alerts"].create_index("linked_user_id")

    except Exception as e:
        print(f"[PANICSA-API-HISTORY] | Could not connect to MongoDB: {e}")
        raise

    yield

    #close the db when api stopes
    if client:
        client.close()


app = FastAPI(lifespan=lifespan)

#allow frontend to talk to us during local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ENV_MONGO_URI = os.environ.get("ENV_MONGO_URI")
ENV_JWT_SECRET = os.environ.get("ENV_JWT_SECRET", "panicsa-dev-jwt-secret-change-me")
JWT_ALGORITHM = "HS256"


def get_current_user_id(request: Request) -> str:
    auth_header = request.headers.get("Authorization", "")

    #gaurd clause if no bearer token
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="[PANICSA-API-HISTORY] | Missing or invalid authorization token.",
        )

    token = auth_header[7:]

    try:
        payload = jwt.decode(token, ENV_JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="[PANICSA-API-HISTORY] | Invalid authorization token.",
            )
        return str(user_id)
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="[PANICSA-API-HISTORY] | Invalid authorization token.",
        )


def serialize_alert(alert_doc: dict) -> AlertResponse:
    return AlertResponse(
        id=str(alert_doc["_id"]),
        alert_id=alert_doc["alert_id"],
        linked_user_id=alert_doc["linked_user_id"],
        latitude=alert_doc["latitude"],
        longitude=alert_doc["longitude"],
        status=alert_doc["status"],
        created_at=alert_doc["created_at"].isoformat(),
        cancel_reason=alert_doc.get("cancel_reason"),
    )


@app.get("/history/alerts/user/{user_id}", response_model=UserAlertsResponse)
def get_user_alerts(request: Request, user_id: str):
    """
    Get all alerts for a user
    """
    #error if the db is not in state
    if not hasattr(request.app.state, "db"):
        raise HTTPException(
            status_code=503,
            detail="[PANICSA-API-HISTORY] | Database connection could not be established.",
        )

    current_user_id = get_current_user_id(request)

    #gaurd clause if user tries to read someone elses alerts
    if current_user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="[PANICSA-API-HISTORY] | You can only view your own alert history.",
        )

    db = request.app.state.db
    alerts = db["alerts"]

    alert_docs = alerts.find({"linked_user_id": user_id}).sort("created_at", -1)

    return UserAlertsResponse(
        status="success",
        message="[PANICSA-API-HISTORY] | Alerts loaded.",
        alerts=[serialize_alert(doc) for doc in alert_docs],
    )
