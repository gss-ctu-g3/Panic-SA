from sqlalchemy import Column, String, CHAR, TIMESTAMP, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(CHAR(36), primary_key=True)
    user_id = Column(CHAR(36), nullable=False)
    status = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    created = Column(
    TIMESTAMP(timezone=True),
    nullable=False,
    default=lambda: datetime.now(timezone.utc)
)