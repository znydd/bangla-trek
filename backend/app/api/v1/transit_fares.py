import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.transit_fare import (
    BookingLinksResponse,
    TransitFareContributionCreate,
    TransitFareContributionList,
    TransitFareContributionRead,
    TransitFareEstimateResponse,
)
from app.services.transit_fare_service import TransitFareService

router = APIRouter(prefix="/transit-fares", tags=["transit-fares"])


@router.get("/estimate", response_model=TransitFareEstimateResponse)
def get_fare_estimate(
    origin: str = Query(..., min_length=1, max_length=255),
    destination: str = Query(..., min_length=1, max_length=255),
    mode: Optional[str] = Query(None, pattern="^(cng|bus|train)$"),
    recent_days: int = Query(180, ge=30, le=365),
    min_recent_samples: int = Query(3, ge=1, le=20),
    db: Session = Depends(get_db),
):
    service = TransitFareService(db)
    return service.get_estimates(
        origin=origin,
        destination=destination,
        mode=mode,
        recent_days=recent_days,
        min_recent_samples=min_recent_samples,
    )


@router.get("/contributions", response_model=TransitFareContributionList)
def list_fare_contributions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    mode: Optional[str] = Query(None, pattern="^(cng|bus|train)$"),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    service = TransitFareService(db)
    items, total = service.list_contributions(
        page=page,
        per_page=per_page,
        origin=origin,
        destination=destination,
        mode=mode,
        date_from=date_from,
        date_to=date_to,
    )
    total_pages = (total + per_page - 1) // per_page
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


@router.post("/contributions", response_model=TransitFareContributionRead)
def create_fare_contribution(
    payload: TransitFareContributionCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = TransitFareService(db)
    try:
        return service.create_contribution(uuid.UUID(user_id), payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.delete("/contributions/{contribution_id}")
def delete_fare_contribution(
    contribution_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = TransitFareService(db)
    try:
        service.delete_contribution(contribution_id, uuid.UUID(user_id))
        return {"detail": "Fare contribution deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/booking-links", response_model=BookingLinksResponse)
def get_booking_links():
    return TransitFareService.get_booking_links()
