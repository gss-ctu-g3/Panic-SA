import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pymongo import MongoClient

from schemas import EmergencyContactCreate, EmergencyContactUpdate


#our custom lifespan as the docs say for db
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[PANICSA-API-CONTACT] | Started")
    mongo_uri = ENV_MONGO_URI
    client: MongoClient[Dict[str, Any]] | None = None
    db: Any | None = None

    try:
        #init the db cleint
        client = MongoClient(mongo_uri)

        #set the client to app state
        app.state.mongo_client = client
        #db is panic_sa for contacts btw
        db = client["panic_sa"]
        #set the db
        app.state.db = db

        #index for listing contacts by user
        db["contacts"].create_index("linked_user_id")

    except Exception as e:
        print(f"[PANICSA-API-CONTACT] | Could not connect to MongoDB: {e}")
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
MAX_CONTACTS_PER_USER = int(os.environ.get("MAX_CONTACTS_PER_USER", "5"))


def get_current_user_id(request: Request) -> str:
    auth_header = request.headers.get("Authorization", "")

    #gaurd clause if no bearer token
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="[PANICSA-API-CONTACT] | Missing or invalid authorization token.",
        )

    token = auth_header[7:]

    try:
        payload = jwt.decode(token, ENV_JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="[PANICSA-API-CONTACT] | Invalid authorization token.",
            )
        return str(user_id)
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="[PANICSA-API-CONTACT] | Invalid authorization token.",
        )


def serialize_contact(contact_doc: dict) -> dict:
    return {
        "id": str(contact_doc["_id"]),
        "linked_user_id": contact_doc["linked_user_id"],
        "name": contact_doc["name"],
        "phone": contact_doc["phone"],
        "email_address": contact_doc["email_address"],
        "relationship": contact_doc["relationship"],
        "created_at": contact_doc["created_at"].isoformat(),
        "updated_at": contact_doc["updated_at"].isoformat(),
    }


def parse_contact_id(contact_id: str) -> ObjectId:
    try:
        return ObjectId(contact_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="[PANICSA-API-CONTACT] | Invalid contact id.",
        )


def get_owned_contact(request: Request, contact_id: str, user_id: str) -> dict:
    #error if the db is not in state
    if not hasattr(request.app.state, "db"):
        raise HTTPException(
            status_code=503,
            detail="[PANICSA-API-CONTACT] | Database connection could not be established.",
        )

    db = request.app.state.db
    contacts = db["contacts"]
    contact_object_id = parse_contact_id(contact_id)

    contact_doc = contacts.find_one({"_id": contact_object_id, "linked_user_id": user_id})

    #gaurd clause if contact not found or not owned by user
    if not contact_doc:
        raise HTTPException(
            status_code=404,
            detail="[PANICSA-API-CONTACT] | Contact not found.",
        )

    return contact_doc


@app.post("/contacts")
def create_emergency_contact(request: Request, contact_json: EmergencyContactCreate):
    """
    Create an emergency contact in database
    """
    #error if the db is not in state
    if not hasattr(request.app.state, "db"):
        raise HTTPException(
            status_code=503,
            detail="[PANICSA-API-CONTACT] | Database connection could not be established.",
        )

    user_id = get_current_user_id(request)
    db = request.app.state.db
    contacts = db["contacts"]

    #gaurd clause if user already has max contacts
    current_count = contacts.count_documents({"linked_user_id": user_id})
    if current_count >= MAX_CONTACTS_PER_USER:
        return {
            "status": "failed",
            "message": f"[PANICSA-API-CONTACT] | Maximum of {MAX_CONTACTS_PER_USER} contacts allowed.",
        }

    now = datetime.now(timezone.utc)
    contact_doc = {
        "linked_user_id": user_id,
        "name": contact_json.name.strip(),
        "phone": contact_json.phone,
        "email_address": str(contact_json.email_address),
        "relationship": contact_json.relationship.strip(),
        "created_at": now,
        "updated_at": now,
    }

    try:
        result = contacts.insert_one(contact_doc)
        contact_doc["_id"] = result.inserted_id
    except Exception as e:
        print(f"[PANICSA-API-CONTACT] | Contact insert failed: {e}")
        return {
            "status": "failed",
            "message": "[PANICSA-API-CONTACT] | Could not create contact.",
        }

    return {
        "status": "success",
        "message": "[PANICSA-API-CONTACT] | Contact created.",
        "contact": serialize_contact(contact_doc),
    }


@app.get("/contacts/user/{user_id}")
def get_user_contacts(request: Request, user_id: str):
    """
    Get all emergency contacts for a user
    """
    #error if the db is not in state
    if not hasattr(request.app.state, "db"):
        raise HTTPException(
            status_code=503,
            detail="[PANICSA-API-CONTACT] | Database connection could not be established.",
        )

    current_user_id = get_current_user_id(request)

    #gaurd clause if user tries to read someone elses contacts
    if current_user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="[PANICSA-API-CONTACT] | You can only view your own contacts.",
        )

    db = request.app.state.db
    contacts = db["contacts"]

    contact_docs = contacts.find({"linked_user_id": user_id}).sort("created_at", 1)

    return {
        "status": "success",
        "message": "[PANICSA-API-CONTACT] | Contacts loaded.",
        "contacts": [serialize_contact(doc) for doc in contact_docs],
    }


@app.get("/contacts/{contact_id}")
def get_emergency_contact(request: Request, contact_id: str):
    """
    Get a single emergency contact
    """
    user_id = get_current_user_id(request)
    contact_doc = get_owned_contact(request, contact_id, user_id)

    return {
        "status": "success",
        "message": "[PANICSA-API-CONTACT] | Contact loaded.",
        "contact": serialize_contact(contact_doc),
    }


@app.put("/contacts/{contact_id}")
def update_emergency_contact(
    request: Request,
    contact_id: str,
    contact_json: EmergencyContactUpdate,
):
    """
    Update an emergency contact
    """
    user_id = get_current_user_id(request)
    get_owned_contact(request, contact_id, user_id)

    update_data = contact_json.model_dump(exclude_none=True)

    #gaurd clause if nothing to update
    if not update_data:
        return {
            "status": "failed",
            "message": "[PANICSA-API-CONTACT] | No update fields provided.",
        }

    if "name" in update_data:
        update_data["name"] = update_data["name"].strip()
    if "relationship" in update_data:
        update_data["relationship"] = update_data["relationship"].strip()
    if "email_address" in update_data:
        update_data["email_address"] = str(update_data["email_address"])

    update_data["updated_at"] = datetime.now(timezone.utc)

    db = request.app.state.db
    contacts = db["contacts"]
    contact_object_id = parse_contact_id(contact_id)

    try:
        contacts.update_one({"_id": contact_object_id}, {"$set": update_data})
        updated_doc = contacts.find_one({"_id": contact_object_id})
    except Exception as e:
        print(f"[PANICSA-API-CONTACT] | Contact update failed: {e}")
        return {
            "status": "failed",
            "message": "[PANICSA-API-CONTACT] | Could not update contact.",
        }

    return {
        "status": "success",
        "message": "[PANICSA-API-CONTACT] | Contact updated.",
        "contact": serialize_contact(updated_doc),
    }


@app.delete("/contacts/{contact_id}")
def delete_emergency_contact(request: Request, contact_id: str):
    """
    Delete an emergency contact
    """
    user_id = get_current_user_id(request)
    get_owned_contact(request, contact_id, user_id)

    db = request.app.state.db
    contacts = db["contacts"]
    contact_object_id = parse_contact_id(contact_id)

    try:
        contacts.delete_one({"_id": contact_object_id, "linked_user_id": user_id})
    except Exception as e:
        print(f"[PANICSA-API-CONTACT] | Contact delete failed: {e}")
        return {
            "status": "failed",
            "message": "[PANICSA-API-CONTACT] | Could not delete contact.",
        }

    return {
        "status": "success",
        "message": "[PANICSA-API-CONTACT] | Contact deleted.",
    }
