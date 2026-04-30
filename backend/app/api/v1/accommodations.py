import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.accommodation import (
    AccommodationListResponse,
    AccommodationRead,
    AIRecommendationsResponse,
)
from app.services.accommodation_service import AccommodationService

router = APIRouter(prefix="/accommodations", tags=["accommodations"])


@router.get("/", response_model=AccommodationListResponse)
def search_accommodations(
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=100),
    accommodation_type: Optional[str] = Query(
        None, description="Filter by type: hotel, guesthouse, homestay"
    ),
    price_range: Optional[str] = Query(
        None, description="Filter by price: budget, mid_range, premium, luxury"
    ),
    amenities: Optional[List[str]] = Query(
        None, description="Filter by amenities (entries must have ALL listed)"
    ),
    search: Optional[str] = Query(None, description="Search by name or location"),
    sort_by: str = Query(
        "newest",
        description="Sort: newest, name, price_asc, price_desc, distance",
    ),
    ref_lat: Optional[float] = Query(
        None, description="Reference latitude for distance calculation"
    ),
    ref_lng: Optional[float] = Query(
        None, description="Reference longitude for distance calculation"
    ),
    db: Session = Depends(get_db),
):
    """Search and filter accommodation entries with pagination."""
    service = AccommodationService(db)
    items, total = service.search_accommodations(
        page=page,
        per_page=per_page,
        accommodation_type=accommodation_type,
        price_range=price_range,
        amenities=amenities,
        search=search,
        sort_by=sort_by,
        ref_lat=ref_lat,
        ref_lng=ref_lng,
    )

    total_pages = (total + per_page - 1) // per_page

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


@router.get("/{entry_id}", response_model=AccommodationRead)
def get_accommodation(entry_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a single accommodation entry by ID."""
    service = AccommodationService(db)
    try:
        return service.get_accommodation(entry_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/itinerary/{itinerary_id}/recommendations",
    response_model=AIRecommendationsResponse,
)
def get_ai_recommendations(
    itinerary_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get AI-powered accommodation recommendations for a specific itinerary."""
    service = AccommodationService(db)
    try:
        return service.get_ai_recommendations(itinerary_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
