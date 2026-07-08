from pydantic import BaseModel

class sms_payload_single(BaseModel):
    send_to: str
    user_full_name: str
    alert_id: str

class sms_payload_multi(BaseModel):
    send_to: list[str]
    user_full_name: str
    alert_id: str