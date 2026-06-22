from datetime import date
from fastapi import APIRouter, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from services.history_service import get_alerts, get_notifications

router = APIRouter()

@router.get("/alerts")
def get_alerts_endpoint(
    user_id: str = Query(None, description="User ID to filter alerts"),
    status: str = Query(None, description="Status to filter alerts"),
    date: date | None = Query(None, description="Date to filter alerts (YYYY-MM-DD)"),
    start_date: date | None = Query(None, description="Start date to filter alerts (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="End date to filter alerts (YYYY-MM-DD)"),
    limit: int = Query(100, description="Maximum number of alerts to return"),
    offset: int = Query(0, description="Number of alerts to skip for pagination"),
):
    alerts = get_alerts(
        user_id=user_id,
        status=status,
        date=date,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    return JSONResponse(content=jsonable_encoder(alerts))


@router.get("/notifications")
def get_notifications_endpoint(
    user_id: str = Query(None, description="User ID to filter notifications"),
    status: str = Query(None, description="Status to filter notifications"),
    date: date | None = Query(None, description="Date to filter notifications (YYYY-MM-DD)"),
    start_date: date | None = Query(None, description="Start date to filter notifications (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="End date to filter notifications (YYYY-MM-DD)"),
    limit: int = Query(100, description="Maximum number of notifications to return"),
    offset: int = Query(0, description="Number of notifications to skip for pagination"),
):
    notifications = get_notifications(
        user_id=user_id,
        status=status,
        date=date,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    return JSONResponse(content=jsonable_encoder(notifications))
