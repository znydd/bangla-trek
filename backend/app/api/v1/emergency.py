from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.emergency import (
    EmergencyFacilityListResponse,
    EmergencyFacilityRead,
    EmergencyPhraseCategoryRead,
    TranslateRequest,
    TranslateResponse,
)
from app.services.emergency_service import EmergencyService

router = APIRouter(prefix="/emergency", tags=["emergency"])


@router.get("/facilities", response_model=EmergencyFacilityListResponse)
def list_facilities(
    facility_type: Optional[str] = Query(
        None, description="Filter: hospital, police_station, tourist_police"
    ),
    district: Optional[str] = Query(None, description="Filter by district"),
    search: Optional[str] = Query(None, description="Search name/address/district"),
    lat: Optional[float] = Query(None, description="User latitude for distance"),
    lng: Optional[float] = Query(None, description="User longitude for distance"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List emergency facilities with optional filters. Provide lat/lng to sort by distance."""
    service = EmergencyService(db)
    items, total = service.list_facilities(
        facility_type=facility_type,
        district=district,
        search=search,
        lat=lat,
        lng=lng,
        limit=limit,
    )
    return {"items": items, "total": total}


@router.get("/facilities/nearest", response_model=List[EmergencyFacilityRead])
def get_nearest_facilities(
    lat: float = Query(..., description="User latitude"),
    lng: float = Query(..., description="User longitude"),
    facility_type: Optional[str] = Query(None, description="Filter by type"),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """Get the nearest emergency facilities from the user's GPS location."""
    service = EmergencyService(db)
    return service.get_nearest_facilities(
        lat=lat, lng=lng, facility_type=facility_type, limit=limit
    )


@router.get("/phrases", response_model=List[EmergencyPhraseCategoryRead])
def get_emergency_phrases(
    db: Session = Depends(get_db),
):
    """Get all pre-saved emergency phrases organized by category."""
    service = EmergencyService(db)
    return service.get_emergency_phrases()


@router.post("/translate", response_model=TranslateResponse)
def translate_phrase(
    payload: TranslateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Translate a custom emergency phrase into Bengali + optional local dialect using AI."""
    service = EmergencyService(db)
    try:
        return service.translate_phrase(payload.text, payload.dialect)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
