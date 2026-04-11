import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.itinerary import (
    ItineraryGenerateRequest,
    ItineraryListItem,
    ItineraryRead,
)
from app.services.itinerary_service import ItineraryService

router = APIRouter(prefix="/itineraries", tags=["itineraries"])


@router.post("/generate", response_model=ItineraryRead)
def generate_itinerary(
    payload: ItineraryGenerateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Generate an AI-powered travel itinerary using Gemini and community data."""
    service = ItineraryService(db)
    try:
        return service.generate_itinerary(uuid.UUID(user_id), payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/", response_model=List[ItineraryListItem])
def list_itineraries(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """List all itineraries for the current user."""
    service = ItineraryService(db)
    return service.list_user_itineraries(uuid.UUID(user_id))


@router.get("/{itinerary_id}", response_model=ItineraryRead)
def get_itinerary(
    itinerary_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get a single itinerary with all activities."""
    service = ItineraryService(db)
    try:
        return service.get_itinerary(itinerary_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{itinerary_id}")
def delete_itinerary(
    itinerary_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Delete an itinerary (owner only)."""
    service = ItineraryService(db)
    try:
        service.delete_itinerary(itinerary_id, uuid.UUID(user_id))
        return {"detail": "Itinerary deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

from pydantic import BaseModel
class ActivityCreate(BaseModel):
    day_number: int
    start_time: str
    end_time: str
    title: str
    description: str
    estimated_cost: float = 0.0
    location: str
    category: str

@router.post("/{itinerary_id}/activities")
def add_activity(
    itinerary_id: uuid.UUID,
    data: ActivityCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    from app.models.itinerary import Itinerary, ItineraryActivity
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
        
    # Basic permission check: if group_trip_id is present, check member
    if itinerary.group_trip_id:
        from app.models.group_trip import GroupTripMember
        is_member = db.query(GroupTripMember).filter(GroupTripMember.trip_id == itinerary.group_trip_id, GroupTripMember.user_id == uuid.UUID(user_id)).first()
        if not is_member:
             raise HTTPException(status_code=403, detail="Must be trip member to edit")
    else:
        if itinerary.user_id != uuid.UUID(user_id):
             raise HTTPException(status_code=403, detail="Must be owner to edit")

    activity = ItineraryActivity(
        itinerary_id=itinerary_id,
        **data.model_dump()
    )
    db.add(activity)
    db.commit()
    
    # Notify if group trip
    if itinerary.group_trip_id:
        from app.models.notification import Notification
        from app.models.group_trip import GroupTripMember
        members = db.query(GroupTripMember).filter(GroupTripMember.trip_id == itinerary.group_trip_id).all()
        for member in members:
            if member.user_id != uuid.UUID(user_id):
                notif = Notification(
                    user_id=member.user_id,
                    type="itinerary_updated",
                    message=f"An activity was added to the itinerary: {activity.title}.",
                    resource_id=itinerary.group_trip_id,
                    resource_type="trip"
                )
                db.add(notif)
        db.commit()

    return activity
