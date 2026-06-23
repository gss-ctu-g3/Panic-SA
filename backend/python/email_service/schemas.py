from pydantic import BaseModel, Field

class EmailPayload(BaseModel):
    #i had it a typeddict but for validation and auto testing later this is better in long run
    #from is resevered so we needed to do this
    from_field: str = Field(alias="from") 
    to: list[str]
    subject: str
    text: str | None = None
    html: str

class EmailConsent(BaseModel):
    send_to: list[str]
    user_full_name: str
    revoke_consent_url: str

class EmailAlert(BaseModel):
    send_to: list[str]
    user_full_name: str
    location_link: str
    revoke_consent_url: str



class UserData(BaseModel):
    username: str
    email: str
    age: int | None = None  # Optional field



