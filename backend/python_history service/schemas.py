from datetime import datetime
from typing import TypedDict

class Alert(TypedDict):
    id: str
    user_id: str
    long: float
    lat: float
    status: str
    created: datetime

class Notification(TypedDict):
    id: str
    user_id: str
    status: str
    message: str
    created: datetime
