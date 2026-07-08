from pydantic import BaseModel


class PanicAlertCreate(BaseModel):
    latitude: float
    longitude: float


class LocationUpdate(BaseModel):
    latitude: float
    longitude: float


class AlertCancel(BaseModel):
    cancel_reason: str
    cancel_reason_detail: str | None = None
