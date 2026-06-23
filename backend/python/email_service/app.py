from fastapi import FastAPI
import requests
import os

from schemas import EmailPayload, EmailConsent, EmailAlert


app = FastAPI()

ENV_DOMAIN_NAME = os.environ.get("ENV_DOMAIN_NAME")
ENV_MAILGUN_API_KEY = os.environ.get("ENV_MAILGUN_API_KEY")
ENV_MAILGUN_FRIENDLY_NAME = os.environ.get("ENV_MAILGUN_FRIENDLY_NAME")
ENV_MAILGUN_FRIENDLY_EMAIL_PREFIX = os.environ.get("ENV_MAILGUN_FRIENDLY_EMAIL_PREFIX")

URL_MAILGUN = f"https://api.mailgun.net/v3/{ENV_DOMAIN_NAME}/messages"
MAILGUN_SENDER = f"{ENV_MAILGUN_FRIENDLY_NAME} <{ENV_MAILGUN_FRIENDLY_EMAIL_PREFIX}@{ENV_DOMAIN_NAME}>"


# get current dir
current_dir = os.path.dirname(os.path.abspath(__file__))


# build template paths
template_consent_path = os.path.join(current_dir, "templates", "consent.html")
template_alert_path = os.path.join(current_dir, "templates", "alert.html")

# make the html templats consants
TEMPLATE_CONSENT: str | None = None
TEMPLATE_ALERT: str | None = None


# read files on start so we dont need to read the templates for eatch req
# its cheaper to just have it on memory than disk io for eatch req
try:
    with open(template_consent_path, "r", encoding="utf-8") as f:
        TEMPLATE_CONSENT = f.read() # type: ignore cuz i cant be bothered i know i am redefining a constant

    with open(template_alert_path, "r", encoding="utf-8") as f:
        TEMPLATE_ALERT = f.read() # type: ignore cuz i cant be bothered i know i am redefining a constant
except:
    print("fuck")



@app.post("/email/consent")
def email_consent(email_json: EmailConsent):

    if (TEMPLATE_CONSENT == None) or (TEMPLATE_ALERT == None):
        return {
            "status" : "Failed",
            "message" : "Error loading templates failing for safety."
        }
    else:
        # init a var to do all the manulipation so we dont override the constant
        template_consent = TEMPLATE_CONSENT

        # building data to replace placeholder data
        placeholder_data = {
            "userfullname": f"{email_json.user_full_name}",
            "unsublink": f"{email_json.revoke_consent_url}",
        }
        
        # replacing the [] placeholders
        for key, value in placeholder_data.items():
            template_consent = template_consent.replace(f"[{key}]", str(value))

        # making the raw payload
        raw_payload = EmailPayload(
            # alias unpacking so it will show "from" when running
            # from is needed for mailguns api so askies if you dont understand
            **{"from": f"{MAILGUN_SENDER}"},
            to=email_json.send_to,
            subject="Consent Notice",
            text=None,
            html=template_consent
        )

        # dumping the paylod so it unpacks the ** to from
        # model comes from the schema.py btw
        payload = raw_payload.model_dump(by_alias=True)


        # making the https request to mailgun servers
        response = requests.post(
            URL_MAILGUN,
            auth=("api", f"{ENV_MAILGUN_API_KEY}"),
            data=payload,
        )


        # handle mailgun with the response codes
        if response.status_code == 200:
            print("Response:", response.json())
            return {
                "status" : "Success",
                "message" : "message was sent."
            }
        else:
            print(f"Failed to send email. Status code: {response.status_code}")
            print("Error Details:", response.text)
            return {
                "status" : "Failed",
                "message" : "message failed sending."
            }




@app.post("/email/alert")
def email_alert(email_json: EmailAlert):

    if (TEMPLATE_CONSENT == None) or (TEMPLATE_ALERT == None):
        return {
            "status" : "Failed",
            "message" : "Error loading templates failing for safety."
        }
    else:
        # init a var to do all the manulipation so we dont override the constant
        template_alert = TEMPLATE_ALERT

        # building data to replace placeholder data
        placeholder_data = {
            "userfullname": f"{email_json.user_full_name}",
            "locationlink" : f"{email_json.location_link}",
            "unsublink": f"{email_json.revoke_consent_url}",
        }
        
        # replacing the [] placeholders
        for key, value in placeholder_data.items():
            template_alert = template_alert.replace(f"[{key}]", str(value))

        # making the raw payload
        raw_payload = EmailPayload(
            # alias unpacking so it will show "from" when running
            # from is needed for mailguns api so askies if you dont understand
            **{"from": f"{MAILGUN_SENDER}"},
            to=email_json.send_to,
            subject="Alert Notice",
            text=None,
            html=template_alert
        )

        # dumping the paylod so it unpacks the ** to from
        # model comes from the schema.py btw
        payload = raw_payload.model_dump(by_alias=True)


        # making the https request to mailgun servers
        response = requests.post(
            URL_MAILGUN,
            auth=("api", f"{ENV_MAILGUN_API_KEY}"),
            data=payload,
        )


        # handle mailgun with the response codes
        if response.status_code == 200:
            print("Response:", response.json())
            return {
                "status" : "Success",
                "message" : "message was sent."
            }
        else:
            print(f"Failed to send email. Status code: {response.status_code}")
            print("Error Details:", response.text)
            return {
                "status" : "Failed",
                "message" : "message failed sending."
            }