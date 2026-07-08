import re

from pydantic import BaseModel, EmailStr, field_validator

SA_PHONE_E164_PATTERN = re.compile(r"^\+27\d{9}$")


def normalize_sa_phone(value: str) -> str:
    #strip junk chars users type in forms
    cleaned = re.sub(r"[\s\-()]", "", value.strip())

    if cleaned.startswith("0") and len(cleaned) == 10:
        cleaned = "+27" + cleaned[1:]
    elif cleaned.startswith("27") and len(cleaned) == 11:
        cleaned = "+" + cleaned
    elif cleaned.startswith("+27") and len(cleaned) == 12:
        pass

    if not SA_PHONE_E164_PATTERN.match(cleaned):
        raise ValueError(
            "Invalid phone number. Use a 10-digit SA number starting with 0, or +27 international format."
        )

    return cleaned


class EmergencyContactCreate(BaseModel):
    name: str
    phone: str
    email_address: EmailStr
    relationship: str

    @field_validator("name", "relationship")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("This field cannot be empty.")
        return cleaned

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return normalize_sa_phone(value)


class EmergencyContactUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email_address: EmailStr | None = None
    relationship: str | None = None

    @field_validator("name", "relationship")
    @classmethod
    def validate_non_empty(cls, value: str | None) -> str | None:
        if value is None:
            return value

        cleaned = value.strip()
        if not cleaned:
            raise ValueError("This field cannot be empty.")
        return cleaned

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return normalize_sa_phone(value)
