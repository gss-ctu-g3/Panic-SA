from sqlalchemy import Column, String, CHAR, Numeric, TIMESTAMP
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(CHAR(36), primary_key=True)
    user_id = Column(CHAR(36), nullable=False)
    long = Column(Numeric(11, 8), nullable=False)
    lat = Column(Numeric(11, 8), nullable=False)
    status = Column(String(20), nullable=False)
    created = Column(
    TIMESTAMP(timezone=True),
    nullable=False,
    default=lambda: datetime.now(timezone.utc)
)

