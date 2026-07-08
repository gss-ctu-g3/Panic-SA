import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Literal

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pymongo import MongoClient


#our custom lifespan as the docs say for db
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[PANICSA-API-ADMIN] | Started")
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

        #index for listing alerts
        db["alerts"].create_index("linked_user_id")
        db["alerts"].create_index("status")
        db["alerts"].create_index("created_at")

    except Exception as e:
        print(f"[PANICSA-API-ADMIN] | Could not connect to MongoDB: {e}")
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
ALLOWED_STATUS_FILTERS = {"active", "cancelled"}


def require_admin(request: Request) -> dict:
    auth_header = request.headers.get("Authorization", "")

    #gaurd clause if no bearer token
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="[PANICSA-API-ADMIN] | Missing or invalid authorization token.",
        )

    token = auth_header[7:]

    try:
        payload = jwt.decode(token, ENV_JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        tags = payload.get("tags", [])

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="[PANICSA-API-ADMIN] | Invalid authorization token.",
            )

        #gaurd clause if user is not an admin
        if not isinstance(tags, list) or "admin" not in tags:
            raise HTTPException(
                status_code=403,
                detail="[PANICSA-API-ADMIN] | Admin access required.",
            )

        return {
            "user_id": str(user_id),
            "tags": tags,
        }
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="[PANICSA-API-ADMIN] | Invalid authorization token.",
        )


def get_db_or_fail(request: Request):
    #error if the db is not in state
    if not hasattr(request.app.state, "db"):
        raise HTTPException(
            status_code=503,
            detail="[PANICSA-API-ADMIN] | Database connection could not be established.",
        )
    return request.app.state.db


def build_location_link(latitude: float, longitude: float) -> str:
    return f"https://www.google.com/maps?q={latitude},{longitude}"


def serialize_alert(alert_doc: dict) -> dict:
    latitude = alert_doc["latitude"]
    longitude = alert_doc["longitude"]

    serialized = {
        "id": str(alert_doc["_id"]),
        "alert_id": alert_doc["alert_id"],
        "linked_user_id": alert_doc["linked_user_id"],
        "latitude": latitude,
        "longitude": longitude,
        "status": alert_doc["status"],
        "created_at": alert_doc["created_at"].isoformat(),
        "location_link": build_location_link(latitude, longitude),
    }

    if alert_doc.get("user_full_name"):
        serialized["user_full_name"] = alert_doc["user_full_name"]

    if alert_doc.get("cancel_reason"):
        serialized["cancel_reason"] = alert_doc["cancel_reason"]

    return serialized


def get_start_of_today_utc() -> datetime:
    now = datetime.now(timezone.utc)
    return datetime(now.year, now.month, now.day, tzinfo=timezone.utc)


def build_status_filter(status: str | None) -> dict:
    if not status or status == "all":
        return {}

    #gaurd clause if status filter is not valid
    if status not in ALLOWED_STATUS_FILTERS:
        raise HTTPException(
            status_code=400,
            detail="[PANICSA-API-ADMIN] | Status filter must be active, cancelled, or all.",
        )

    return {"status": status}


@app.get("/admin/alerts")
def get_all_alerts(
    request: Request,
    status: Literal["all", "active", "cancelled"] | None = Query(default="all"),
):
    """
    Get all alerts across users for the admin dashboard
    """
    require_admin(request)
    db = get_db_or_fail(request)
    alerts = db["alerts"]

    query_filter = build_status_filter(status)
    alert_docs = alerts.find(query_filter).sort("created_at", -1)

    return {
        "status": "success",
        "message": "[PANICSA-API-ADMIN] | Alerts loaded.",
        "alerts": [serialize_alert(doc) for doc in alert_docs],
    }


@app.get("/admin/stats")
def get_admin_stats(request: Request):
    """
    Get alert statistics for the admin dashboard
    """
    require_admin(request)
    db = get_db_or_fail(request)
    alerts = db["alerts"]

    start_of_today = get_start_of_today_utc()

    return {
        "status": "success",
        "message": "[PANICSA-API-ADMIN] | Stats loaded.",
        "stats": {
            "total_alerts": alerts.count_documents({}),
            "today_alerts": alerts.count_documents({"created_at": {"$gte": start_of_today}}),
            "active_alerts": alerts.count_documents({"status": "active"}),
        },
    }
