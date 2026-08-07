import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.trip import (
    EmailDraftRead,
    TravelTripCreate,
    TravelTripDetailRead,
    TravelTripParticipantRead,
    TravelTripRead,
    TravelTripUpdate,
)
from app.services.trip_service import TripService

router = APIRouter(prefix="/travel-trips", tags=["travel-trips"])


@router.get("", response_model=List[TravelTripRead])
async def list_travel_trips(
    origin: Optional[str] = Query(None, description="Filter by origin city"),
    destination: Optional[str] = Query(None, description="Filter by destination city"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Public API: List active public travel buddy trips."""
    trip_svc = TripService(db)
    return trip_svc.list_public_trips(
        origin=origin, destination=destination, skip=skip, limit=limit
    )


@router.get("/{trip_id}", response_model=TravelTripDetailRead)
async def get_travel_trip_detail(trip_id: uuid.UUID, db: Session = Depends(get_db)):
    """Public API: Get detailed public trip info with public member cards (NO emails exposed)."""
    trip_svc = TripService(db)
    return trip_svc.get_trip_detail(trip_id)


@router.post("", response_model=TravelTripDetailRead)
async def create_travel_trip(
    trip_in: TravelTripCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: Create a new public travel buddy trip."""
    trip_svc = TripService(db)
    return trip_svc.create_trip(creator_id=current_user.id, trip_in=trip_in)


@router.patch("/{trip_id}", response_model=TravelTripDetailRead)
async def update_travel_trip(
    trip_id: uuid.UUID,
    update_in: TravelTripUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: Update trip details (Organizer only)."""
    trip_svc = TripService(db)
    return trip_svc.update_trip(
        trip_id=trip_id, organizer_id=current_user.id, update_in=update_in
    )


@router.post("/{trip_id}/join", response_model=TravelTripDetailRead)
async def join_travel_trip(
    trip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: Join a travel buddy trip with row-locked capacity check."""
    trip_svc = TripService(db)
    return trip_svc.join_trip_transactional(trip_id=trip_id, user_id=current_user.id)


@router.delete("/{trip_id}/membership")
async def leave_travel_trip(
    trip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: Leave a joined trip."""
    trip_svc = TripService(db)
    return trip_svc.leave_trip(trip_id=trip_id, user_id=current_user.id)


@router.post("/{trip_id}/cancel")
async def cancel_travel_trip(
    trip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: Cancel a trip (Organizer only)."""
    trip_svc = TripService(db)
    return trip_svc.cancel_trip(trip_id=trip_id, organizer_id=current_user.id)


@router.get("/{trip_id}/participants", response_model=List[TravelTripParticipantRead])
async def list_trip_participants(
    trip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: List participant contacts with emails (ORGANIZER ONLY)."""
    trip_svc = TripService(db)
    return trip_svc.get_organizer_participants(
        trip_id=trip_id, organizer_id=current_user.id
    )


@router.get("/{trip_id}/email-draft", response_model=EmailDraftRead)
async def get_trip_email_draft(
    trip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: Generate BCC mailto draft for participants (ORGANIZER ONLY)."""
    trip_svc = TripService(db)
    return trip_svc.get_organizer_email_draft(
        trip_id=trip_id, organizer_id=current_user.id
    )
