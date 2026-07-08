import requests
from requests.auth import HTTPBasicAuth
from pymongo import MongoClient
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from schemas import sms_payload_multi, sms_payload_single
from contextlib import asynccontextmanager
from typing import Dict, Any
import os

#our custom lifespan as the docs say for db 
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[PANICSA-API-SMS] | Started")
    mongo_uri = ENV_MONGO_URI
    client: MongoClient[Dict[str, Any]] | None = None
    db: Any | None = None

    try:
        #init the db cleint
        client = MongoClient(mongo_uri)
        
        #set the client to app state
        app.state.mongo_client = client
        #db is sms for this service btw
        db = client["sms"]
        #set the db
        app.state.db = db

    except Exception as e:
        print(f"Could not connect to MongoDB: {e}")
        raise 

    yield

    #close the db when api stopes
    if client:
        client.close()

app = FastAPI(lifespan=lifespan)



ENV_MONGO_URI = os.environ.get("ENV_MONGO_URI")
ENV_TOKEN_ID_SMS = os.environ.get("ENV_TOKEN_ID_SMS")
ENV_TOKEN_SECRET_SMS = os.environ.get("ENV_TOKEN_SECRET_SMS")

url = "https://api.bulksms.com/v1/messages"

@app.post("/sms/send")
def sms_single(request: Request, sms_single_json: sms_payload_single):
    """Sends a single SMS alert notification"""
    #error if the db is not in state
    if not hasattr(request.app.state, 'db'):
        #raise 503 if the db is not in state
        raise HTTPException(
            status_code=503,
            detail="[PANICSA-API-SMS] | Database connection could not be established."
        )
    
    db = request.app.state.db 
    logs = None

    try:
        logs = db["logs"] 

        #our payload to sms req
        json_payload = {
            "to": f"{sms_single_json.send_to}",
            "body": f"Panic SA\n{sms_single_json.user_full_name} has triggered a alert.\nView at https://gss-panic-sa.pixieoflife.co.za/alert/live/{sms_single_json.alert_id}"
        }
        
        #send the sms
        response = requests.post(
            url,
            json=json_payload,
            auth=HTTPBasicAuth(
                f"{ENV_TOKEN_ID_SMS}",
                f"{ENV_TOKEN_SECRET_SMS}"
            )
        )

        #make sure we only prosess the data its 201 from sms provider
        #so we gaurd clause it
        if response.status_code != 201:
            return {
                "status" : "failed",
                "message" : "[PANICSA-API-SMS] | sms provider responce was not as expected.\nfailing data processing for safty."
            }


        data = response.json()
        count_success = 0

        #loop tru all the reposnces and log them to db and count the accpted numbers
        for message in data:
            logs.insert_one(
                {
                    "timestamp": datetime.now(),
                    "http_status": response.status_code,
                    **message
                }
            )
            status = message.get("status", {}).get("type")
            if status == "ACCEPTED":
                count_success += 1

        return {
            "status" : "success",
            "message" : f"[PANICSA-API-SMS] | {count_success} sms's were sent."
        }
    
    except:
        return {
            "status" : "failed",
            "message" : "[PANICSA-API-SMS] | Data could not be processed"
        }

    

    



@app.post("/sms/bulk")
def sms_bulk(request: Request, sms_multi_json: sms_payload_multi):
    """Sends multiple SMS alert notifications"""
    #error if the db is not in state
    if not hasattr(request.app.state, 'db'):
        #raise 503 if the db is not in state
        raise HTTPException(
            status_code=503,
            detail="[PANICSA-API-SMS] | Database connection could not be established."
        )
    
    db = request.app.state.db 
    logs = None

    try:
        logs = db["logs"] 

        #this will unpack the json list to a python list
        send_to_list = sms_multi_json.send_to

        #our payload to sms req
        json_payload: Dict[str, Any] = {
            "to": send_to_list,
            "body": f"Panic SA\n{sms_multi_json.user_full_name} has triggered a alert.\nView at https://gss-panic-sa.pixieoflife.co.za/alert/live/{sms_multi_json.alert_id}"
        }

        print(json_payload)
        
        #send the sms
        response = requests.post(
            url,
            json=json_payload,
            auth=HTTPBasicAuth(
                f"{ENV_TOKEN_ID_SMS}",
                f"{ENV_TOKEN_SECRET_SMS}"
            )
        )

        #make sure we only prosess the data its 201 from sms provider
        #so we gaurd clause it
        if response.status_code != 201:
            return {
                "status" : "failed",
                "message" : "[PANICSA-API-SMS] | sms provider responce was not as expected.\nfailing data processing for safty."
            }


        data = response.json()
        count_success = 0
        
        #loop tru all the reposnces and log them to db and count the accpted numbers
        for message in data:
            logs.insert_one(
                {
                    "timestamp": datetime.now(),
                    "http_status": response.status_code,
                    **message
                }
            )
            status = message.get("status", {}).get("type")
            if status == "ACCEPTED":
                count_success += 1

        return {
            "status" : "success",
            "message" : f"[PANICSA-API-SMS] | {count_success} sms's were sent."
        }

    except:
        return {
            "status" : "failed",
            "message" : "[PANICSA-API-SMS] | Data could not be processed"
        }
