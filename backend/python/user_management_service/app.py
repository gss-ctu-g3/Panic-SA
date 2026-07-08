import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import bcrypt
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from pymongo import MongoClient

from schemas import LoginPayload, SignupPayload


#our custom lifespan as the docs say for db
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[PANICSA-API-USER] | Started")
    mongo_uri = ENV_MONGO_URI
    client: MongoClient[Dict[str, Any]] | None = None
    db: Any | None = None

    try:
        #init the db cleint
        client = MongoClient(mongo_uri)

        #set the client to app state
        app.state.mongo_client = client
        #db is panic_sa for users btw
        db = client["panic_sa"]
        #set the db
        app.state.db = db

        #make sure usernames are unique so we dont get dup accounts
        db["users"].create_index("username", unique=True)

    except Exception as e:
        print(f"[PANICSA-API-USER] | Could not connect to MongoDB: {e}")
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

#password hashing stuff
ENV_JWT_SECRET = os.environ.get("ENV_JWT_SECRET", "panicsa-dev-jwt-secret-change-me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user_id: str, username: str, tags: list[str]) -> str:
    #token lasts 7 days so users stay logged in
    expire = datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "username": username,
        "tags": tags,
        "exp": expire,
    }
    return jwt.encode(payload, ENV_JWT_SECRET, algorithm=JWT_ALGORITHM)


def build_auth_response(user_doc: dict) -> dict:
    user_id = str(user_doc["_id"])
    username = user_doc["username"]
    tags = user_doc.get("tags", [])
    token = create_access_token(user_id, username, tags)

    return {
        "status": "success",
        "message": "[PANICSA-API-USER] | Authentication successful.",
        "token": token,
        "userId": user_id,
        "username": username,
        "tags": tags,
    }


@app.post("/auth/signup")
def signup(request: Request, signup_json: SignupPayload):
    """
    Create a new user account and return a login token
    """
    #error if the db is not in state
    if not hasattr(request.app.state, "db"):
        raise HTTPException(
            status_code=503,
            detail="[PANICSA-API-USER] | Database connection could not be established.",
        )

    db = request.app.state.db
    users = db["users"]

    username = signup_json.username.strip()

    #gaurd clause if username already taken
    existing_user = users.find_one({"username": username})
    if existing_user:
        return {
            "status": "failed",
            "message": "[PANICSA-API-USER] | Username already exists.",
        }

    now = datetime.now(timezone.utc)
    user_doc = {
        "username": username,
        "password_hash": hash_password(signup_json.password),
        "tags": [],
        "created_at": now,
        "updated_at": now,
    }

    try:
        result = users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
    except Exception as e:
        print(f"[PANICSA-API-USER] | Signup insert failed: {e}")
        return {
            "status": "failed",
            "message": "[PANICSA-API-USER] | Could not create user account.",
        }

    return build_auth_response(user_doc)


@app.post("/auth/login")
def login(request: Request, login_json: LoginPayload):
    """
    Log in an existing user and return a token
    """
    #error if the db is not in state
    if not hasattr(request.app.state, "db"):
        raise HTTPException(
            status_code=503,
            detail="[PANICSA-API-USER] | Database connection could not be established.",
        )

    db = request.app.state.db
    users = db["users"]

    username = login_json.username.strip()
    user_doc = users.find_one({"username": username})

    #gaurd clause if user not found or password wrong
    if not user_doc or not verify_password(login_json.password, user_doc["password_hash"]):
        return {
            "status": "failed",
            "message": "[PANICSA-API-USER] | Invalid username or password.",
        }

    return build_auth_response(user_doc)
