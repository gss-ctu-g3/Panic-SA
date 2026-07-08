from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: str
    alert_id: str
    linked_user_id: str
    latitude: float
    longitude: float
    status: str
    created_at: str
    cancel_reason: str | None = None


class UserAlertsResponse(BaseModel):
    status: str
    message: str
    alerts: list[AlertResponse]
