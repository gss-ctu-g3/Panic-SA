import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pymongo import MongoClient

from schemas import AlertCancel, LocationUpdate, PanicAlertCreate


#our custom lifespan as the docs say for db
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[PANICSA-API-ALERT] | Started")
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

        #index for looking up alerts
        db["alerts"].create_index("alert_id", unique=True)
        db["alerts"].create_index("linked_user_id")
        db["notification_logs"].create_index("alert_id")
        db["notification_logs"].create_index("linked_user_id")

    except Exception as e:
        print(f"[PANICSA-API-ALERT] | Could not connect to MongoDB: {e}")
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
ENV_CONTACT_SERVICE_URL = os.environ.get(
    "ENV_CONTACT_SERVICE_URL", "http://contact_management:8000"
)
ENV_SMS_SERVICE_URL = os.environ.get("ENV_SMS_SERVICE_URL", "http://sms_service:8000")
ENV_EMAIL_SERVICE_URL = os.environ.get(
    "ENV_EMAIL_SERVICE_URL", "http://email_service:8000"
)
ALLOWED_CANCEL_REASONS = {
    "I am safe now",
    "Triggered by mistake",
    "Help has arrived",
    "Other",
}


def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("Authorization", "")

    #gaurd clause if no bearer token
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="[PANICSA-API-ALERT] | Missing or invalid authorization token.",
        )

    token = auth_header[7:]

    try:
        payload = jwt.decode(token, ENV_JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        username = payload.get("username")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="[PANICSA-API-ALERT] | Invalid authorization token.",
            )
        return {
            "user_id": str(user_id),
            "username": str(username or "Panic SA User"),
        }
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="[PANICSA-API-ALERT] | Invalid authorization token.",
        )


def build_location_link(latitude: float, longitude: float) -> str:
    return f"https://www.google.com/maps?q={latitude},{longitude}"


def resolve_cancel_reason(cancel_json: AlertCancel) -> str:
    reason = cancel_json.cancel_reason.strip()

    #gaurd clause if reason is not in our allow-list
    if reason not in ALLOWED_CANCEL_REASONS:
        raise HTTPException(
            status_code=400,
            detail="[PANICSA-API-ALERT] | Invalid cancel reason.",
        )

    if reason == "Other":
        detail = (cancel_json.cancel_reason_detail or "").strip()

        #gaurd clause if other reason has no detail
        if len(detail) < 5:
            raise HTTPException(
                status_code=400,
                detail="[PANICSA-API-ALERT] | Please provide a cancel reason detail of at least 5 characters.",
            )

        return f"Other: {detail}"

    return reason


def serialize_alert(alert_doc: dict) -> dict:
    latitude = alert_doc["latitude"]
    longitude = alert_doc["longitude"]

    serialized = {
        "id": str(alert_doc["_id"]),
        "alert_id": alert_doc["alert_id"],
        "linked_user_id": alert_doc["linked_user_id"],
        "user_full_name": alert_doc.get("user_full_name", "Panic SA User"),
        "latitude": latitude,
        "longitude": longitude,
        "status": alert_doc["status"],
        "created_at": alert_doc["created_at"].isoformat(),
        "updated_at": alert_doc["updated_at"].isoformat(),
        "location_link": build_location_link(latitude, longitude),
    }

    if alert_doc.get("cancel_reason"):
        serialized["cancel_reason"] = alert_doc["cancel_reason"]

    if alert_doc.get("cancelled_at"):
        serialized["cancelled_at"] = alert_doc["cancelled_at"].isoformat()

    return serialized


def serialize_public_alert(alert_doc: dict) -> dict:
    latitude = alert_doc["latitude"]
    longitude = alert_doc["longitude"]

    return {
        "alert_id": alert_doc["alert_id"],
        "user_full_name": alert_doc.get("user_full_name", "Panic SA User"),
        "latitude": latitude,
        "longitude": longitude,
        "status": alert_doc["status"],
        "updated_at": alert_doc["updated_at"].isoformat(),
        "location_link": build_location_link(latitude, longitude),
    }


def get_owned_active_alert(request: Request, alert_id: str, user_id: str) -> dict:
    #error if the db is not in state
    if not hasattr(request.app.state, "db"):
        raise HTTPException(
            status_code=503,
            detail="[PANICSA-API-ALERT] | Database connection could not be established.",
        )

    db = request.app.state.db
    alerts = db["alerts"]

    alert_doc = alerts.find_one({"alert_id": alert_id})

    #gaurd clause if alert does not exist
    if not alert_doc:
        raise HTTPException(
            status_code=404,
            detail="[PANICSA-API-ALERT] | Alert not found.",
        )

    #gaurd clause if user tries to change someone elses alert
    if alert_doc["linked_user_id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="[PANICSA-API-ALERT] | You can only manage your own alerts.",
        )

    return alert_doc


def fetch_user_contacts(user_id: str, auth_header: str) -> list[dict]:
    response = requests.get(
        f"{ENV_CONTACT_SERVICE_URL}/contacts/user/{user_id}",
        headers={"Authorization": auth_header},
        timeout=10,
    )

    if response.status_code != 200:
        print(
            f"[PANICSA-API-ALERT] | Could not fetch contacts. Status: {response.status_code}"
        )
        return []

    data = response.json()
    if data.get("status") != "success":
        print(f"[PANICSA-API-ALERT] | Contact service failed: {data.get('message')}")
        return []

    return data.get("contacts", [])


def log_notification(
    db: Any,
    alert_id: str,
    user_id: str,
    channel: str,
    recipient: str,
    status: str,
    provider_response: str,
) -> None:
    db["notification_logs"].insert_one(
        {
            "alert_id": alert_id,
            "linked_user_id": user_id,
            "channel": channel,
            "recipient": recipient,
            "status": status,
            "provider_response": provider_response,
            "created_at": datetime.now(timezone.utc),
        }
    )


def send_sms_notifications(
    db: Any,
    alert_id: str,
    user_id: str,
    phones: list[str],
    user_full_name: str,
) -> dict:
    counts = {"sms_sent": 0, "sms_failed": 0, "sms_skipped": 0}

    if not phones:
        log_notification(
            db,
            alert_id,
            user_id,
            "sms",
            "",
            "skipped",
            "No emergency contacts with phone numbers.",
        )
        counts["sms_skipped"] = 1
        return counts

    try:
        response = requests.post(
            f"{ENV_SMS_SERVICE_URL}/sms/bulk",
            json={
                "send_to": phones,
                "user_full_name": user_full_name,
                "alert_id": alert_id,
            },
            timeout=15,
        )

        response_text = f"HTTP {response.status_code}"
        try:
            response_data = response.json()
            response_text = f"{response_text} | {response_data.get('message', response_data)}"
        except Exception:
            response_text = f"{response_text} | {response.text[:200]}"

        sms_status = "success" if response.status_code == 200 else "failed"
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("status") != "success":
                    sms_status = "failed"
            except Exception:
                pass

        for phone in phones:
            log_notification(
                db,
                alert_id,
                user_id,
                "sms",
                phone,
                sms_status,
                response_text,
            )
            if sms_status == "success":
                counts["sms_sent"] += 1
            else:
                counts["sms_failed"] += 1

        print(f"[PANICSA-API-ALERT] | SMS response: {response.status_code}")
    except Exception as e:
        error_text = str(e)
        for phone in phones:
            log_notification(
                db,
                alert_id,
                user_id,
                "sms",
                phone,
                "failed",
                error_text,
            )
            counts["sms_failed"] += 1
        print(f"[PANICSA-API-ALERT] | SMS notification failed: {e}")

    return counts


def send_email_notifications(
    db: Any,
    alert_id: str,
    user_id: str,
    emails: list[str],
    user_full_name: str,
    location_link: str,
) -> dict:
    counts = {"email_sent": 0, "email_failed": 0, "email_skipped": 0}

    if not emails:
        log_notification(
            db,
            alert_id,
            user_id,
            "email",
            "",
            "skipped",
            "No emergency contacts with email addresses.",
        )
        counts["email_skipped"] = 1
        return counts

    try:
        response = requests.post(
            f"{ENV_EMAIL_SERVICE_URL}/email/alert",
            json={
                "send_to": emails,
                "user_full_name": user_full_name,
                "location_link": location_link,
                "revoke_consent_url": "https://gss-panic-sa.pixieoflife.co.za/contacts.html",
            },
            timeout=15,
        )

        response_text = f"HTTP {response.status_code}"
        try:
            response_data = response.json()
            response_text = f"{response_text} | {response_data.get('message', response_data)}"
        except Exception:
            response_text = f"{response_text} | {response.text[:200]}"

        email_status = "success" if response.status_code == 200 else "failed"
        if response.status_code == 200:
            try:
                data = response.json()
                if str(data.get("status", "")).lower() != "success":
                    email_status = "failed"
            except Exception:
                pass

        for email in emails:
            log_notification(
                db,
                alert_id,
                user_id,
                "email",
                email,
                email_status,
                response_text,
            )
            if email_status == "success":
                counts["email_sent"] += 1
            else:
                counts["email_failed"] += 1

        print(f"[PANICSA-API-ALERT] | Email response: {response.status_code}")
    except Exception as e:
        error_text = str(e)
        for email in emails:
            log_notification(
                db,
                alert_id,
                user_id,
                "email",
                email,
                "failed",
                error_text,
            )
            counts["email_failed"] += 1
        print(f"[PANICSA-API-ALERT] | Email notification failed: {e}")

    return counts


@app.post("/alerts/panic")
def trigger_panic_alert(request: Request, panic_json: PanicAlertCreate):
    """
    Trigger a panic alert and notify emergency contacts
    """
    #error if the db is not in state
    if not hasattr(request.app.state, "db"):
        raise HTTPException(
            status_code=503,
            detail="[PANICSA-API-ALERT] | Database connection could not be established.",
        )

    current_user = get_current_user(request)
    user_id = current_user["user_id"]
    user_full_name = current_user["username"]

    db = request.app.state.db
    alerts = db["alerts"]

    #gaurd clause if user already has an active alert
    existing_alert = alerts.find_one(
        {"linked_user_id": user_id, "status": "active"}
    )
    if existing_alert:
        raise HTTPException(
            status_code=409,
            detail="[PANICSA-API-ALERT] | You already have an active alert. Cancel it first.",
        )

    now = datetime.now(timezone.utc)
    alert_id = uuid4().hex[:12]

    alert_doc = {
        "alert_id": alert_id,
        "linked_user_id": user_id,
        "user_full_name": user_full_name,
        "latitude": panic_json.latitude,
        "longitude": panic_json.longitude,
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }

    alerts.insert_one(alert_doc)

    #re-fetch so _id is always present for serialize_alert
    saved_alert = alerts.find_one({"alert_id": alert_id})
    if not saved_alert:
        raise HTTPException(
            status_code=500,
            detail="[PANICSA-API-ALERT] | Alert could not be saved.",
        )

    auth_header = request.headers.get("Authorization", "")
    contacts = fetch_user_contacts(user_id, auth_header)

    phones = [
        contact["phone"]
        for contact in contacts
        if contact.get("phone")
    ]
    emails = [
        contact["email_address"]
        for contact in contacts
        if contact.get("email_address")
    ]

    location_link = build_location_link(panic_json.latitude, panic_json.longitude)

    sms_counts = send_sms_notifications(
        db, alert_id, user_id, phones, user_full_name
    )
    email_counts = send_email_notifications(
        db, alert_id, user_id, emails, user_full_name, location_link
    )

    return {
        "status": "success",
        "message": "[PANICSA-API-ALERT] | Panic alert triggered.",
        "alert": serialize_alert(saved_alert),
        "notifications": {**sms_counts, **email_counts},
    }


@app.get("/alerts/active/me")
def get_active_alert_for_user(request: Request):
    """
    Get the current user's active alert
    """
    #error if the db is not in state
    if not hasattr(request.app.state, "db"):
        raise HTTPException(
            status_code=503,
            detail="[PANICSA-API-ALERT] | Database connection could not be established.",
        )

    current_user = get_current_user(request)
    db = request.app.state.db
    alerts = db["alerts"]

    alert_doc = alerts.find_one(
        {"linked_user_id": current_user["user_id"], "status": "active"}
    )

    if not alert_doc:
        return {
            "status": "success",
            "message": "[PANICSA-API-ALERT] | No active alert.",
            "alert": None,
        }

    return {
        "status": "success",
        "message": "[PANICSA-API-ALERT] | Active alert loaded.",
        "alert": serialize_alert(alert_doc),
    }


@app.get("/alerts/{alert_id}")
def get_alert(alert_id: str, request: Request):
    """
    Public live alert view for emergency contacts
    """
    #error if the db is not in state
    if not hasattr(request.app.state, "db"):
        raise HTTPException(
            status_code=503,
            detail="[PANICSA-API-ALERT] | Database connection could not be established.",
        )

    db = request.app.state.db
    alerts = db["alerts"]

    alert_doc = alerts.find_one({"alert_id": alert_id})

    #gaurd clause if alert does not exist
    if not alert_doc:
        raise HTTPException(
            status_code=404,
            detail="[PANICSA-API-ALERT] | Alert not found.",
        )

    #gaurd clause if alert was cancelled
    if alert_doc["status"] == "cancelled":
        raise HTTPException(
            status_code=410,
            detail="[PANICSA-API-ALERT] | Alert has ended.",
        )

    return {
        "status": "success",
        "message": "[PANICSA-API-ALERT] | Alert loaded.",
        "alert": serialize_public_alert(alert_doc),
    }


@app.patch("/alerts/{alert_id}/location")
def update_alert_location(
    request: Request,
    alert_id: str,
    location_json: LocationUpdate,
):
    """
    Update GPS coordinates for an active alert
    """
    current_user = get_current_user(request)
    alert_doc = get_owned_active_alert(request, alert_id, current_user["user_id"])

    #gaurd clause if alert is not active anymore
    if alert_doc["status"] != "active":
        raise HTTPException(
            status_code=409,
            detail="[PANICSA-API-ALERT] | Alert is no longer active.",
        )

    db = request.app.state.db
    alerts = db["alerts"]
    now = datetime.now(timezone.utc)

    alerts.update_one(
        {"alert_id": alert_id},
        {
            "$set": {
                "latitude": location_json.latitude,
                "longitude": location_json.longitude,
                "updated_at": now,
            }
        },
    )

    updated_alert = alerts.find_one({"alert_id": alert_id})

    return {
        "status": "success",
        "message": "[PANICSA-API-ALERT] | Alert location updated.",
        "alert": serialize_alert(updated_alert),
    }


@app.post("/alerts/{alert_id}/cancel")
def cancel_alert(request: Request, alert_id: str, cancel_json: AlertCancel):
    """
    Cancel an active panic alert
    """
    current_user = get_current_user(request)
    alert_doc = get_owned_active_alert(request, alert_id, current_user["user_id"])

    #gaurd clause if alert is not active anymore
    if alert_doc["status"] != "active":
        return {
            "status": "failed",
            "message": "[PANICSA-API-ALERT] | Alert is already cancelled.",
        }

    cancel_reason = resolve_cancel_reason(cancel_json)

    db = request.app.state.db
    alerts = db["alerts"]
    now = datetime.now(timezone.utc)

    alerts.update_one(
        {"alert_id": alert_id},
        {
            "$set": {
                "status": "cancelled",
                "cancel_reason": cancel_reason,
                "cancelled_at": now,
                "updated_at": now,
            }
        },
    )

    updated_alert = alerts.find_one({"alert_id": alert_id})

    return {
        "status": "success",
        "message": "[PANICSA-API-ALERT] | Alert cancelled.",
        "alert": serialize_alert(updated_alert),
    }
