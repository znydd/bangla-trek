import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id, get_db
from app.schemas.group_collaboration import (
    GroupActivityRead,
    ItineraryLinkRequest,
    PollCreate,
    PollRead,
)
from app.services.group_collaboration_service import CollaborationService

router = APIRouter(tags=["group-collaboration"])


@router.get("/group-trips/{trip_id}/activity", response_model=List[GroupActivityRead])
def get_trip_activity(
    trip_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Fetch the activity feed for a group trip."""
    service = CollaborationService(db)
    if not service.is_member(trip_id, uuid.UUID(user_id)):
        raise HTTPException(status_code=403, detail="Not a member of this trip")
    
    return service.get_activity_feed(trip_id, limit)


@router.post("/group-trips/{trip_id}/polls", response_model=PollRead)
def create_trip_poll(
    trip_id: uuid.UUID,
    payload: PollCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Create a new poll for trip members."""
    service = CollaborationService(db)
    if not service.is_member(trip_id, uuid.UUID(user_id)):
        raise HTTPException(status_code=403, detail="Not a member of this trip")
    
    return service.create_poll(trip_id, uuid.UUID(user_id), payload)


@router.get("/group-trips/{trip_id}/polls", response_model=List[PollRead])
def get_trip_polls(
    trip_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """List all polls for a group trip with current results."""
    service = CollaborationService(db)
    if not service.is_member(trip_id, uuid.UUID(user_id)):
        raise HTTPException(status_code=403, detail="Not a member of this trip")
    
    return service.get_polls(trip_id, uuid.UUID(user_id))


@router.post("/polls/{poll_id}/vote")
def vote_in_poll(
    poll_id: uuid.UUID,
    option_id: uuid.UUID = Query(...),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Cast or change a vote in a poll."""
    service = CollaborationService(db)
    # Check if user is member of the trip this poll belongs to
    from app.models.poll import Poll
    poll = db.get(Poll, poll_id)
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
        
    if not service.is_member(poll.trip_id, uuid.UUID(user_id)):
        raise HTTPException(status_code=403, detail="Not a member of this trip")
    
    try:
        service.vote(poll_id, uuid.UUID(user_id), option_id)
        return {"message": "Vote recorded"}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.patch("/group-trips/{trip_id}/itinerary")
def link_trip_itinerary(
    trip_id: uuid.UUID,
    payload: ItineraryLinkRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Link an itinerary to a group trip (Creator only)."""
    service = CollaborationService(db)
    try:
        service.link_itinerary(trip_id, uuid.UUID(user_id), payload.itinerary_id)
        return {"message": "Itinerary linked successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
