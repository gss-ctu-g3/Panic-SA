from datetime import date
from typing import Any, List, Optional, Type, Union
from sqlalchemy import and_, cast, Date
from database import SessionLocal
from models.alerts import Alert
from models.notifications import Notification


FilterModel = Union[Type[Alert], Type[Notification]]


def _apply_filters(
    query: Any,
    model: FilterModel,
    user_id: Optional[str],
    status: Optional[str],
    date: Optional[date],
    start_date: Optional[date],
    end_date: Optional[date]
) -> Any:
    filters: list[Any] = []

    if user_id:
        filters.append(model.user_id == user_id)

    if status:
        filters.append(model.status == status)

    if date:
        filters.append(cast(model.created, Date) == date)

    if start_date:
        filters.append(cast(model.created, Date) >= start_date)

    if end_date:
        filters.append(cast(model.created, Date) <= end_date)

    if filters:
        query = query.filter(and_(*filters))

    return query


def get_alerts(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Alert]:
    with SessionLocal() as session:
        query = session.query(Alert)
        query = _apply_filters(
            query,
            Alert,
            user_id,
            status,
            date,
            start_date,
            end_date
        )
        return query.order_by(Alert.created.desc()).offset(offset).limit(limit).all()


def get_notifications(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Notification]:
    with SessionLocal() as session:
        query = session.query(Notification)
        query = _apply_filters(
            query,
            Notification,
            user_id,
            status,
            date,
            start_date,
            end_date
        )
        return query.order_by(Notification.created.desc()).offset(offset).limit(limit).all()