import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.group_trip import (
    GroupTripCreate,
    GroupTripDetail,
    GroupTripList,
    GroupTripPreview,
    GroupTripRead,
    GroupTripUpdate,
    OverlappingTrip,
)
from app.services.group_trip_service import GroupTripService

router = APIRouter(prefix="/group-trips", tags=["group-trips"])


@router.post("/", response_model=GroupTripRead)
def create_trip(
    payload: GroupTripCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = GroupTripService(db)
    trip = service.create_trip(uuid.UUID(user_id), payload)

    # Return with creator info
    return service.get_trip_detail(trip.id)


@router.get("/", response_model=GroupTripList)
def list_public_trips(
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """List all public trips."""
    service = GroupTripService(db)
    items, total = service.list_public_trips(page=page, per_page=per_page)
    total_pages = (total + per_page - 1) // per_page
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


@router.get("/my", response_model=GroupTripList)
def list_my_trips(
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """List trips the current user has created or joined."""
    service = GroupTripService(db)
    items, total = service.list_my_trips(
        uuid.UUID(user_id), page=page, per_page=per_page
    )
    total_pages = (total + per_page - 1) // per_page
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


@router.get("/discover", response_model=List[OverlappingTrip])
def discover_overlapping(
    destination: str = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = GroupTripService(db)
    return service.discover_overlapping(
        uuid.UUID(user_id), destination, start_date, end_date
    )


@router.get("/invite/{invite_code}/preview", response_model=GroupTripPreview)
def invite_preview(
    invite_code: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Basic trip info for someone deciding whether to join via invite link."""
    service = GroupTripService(db)
    try:
        return service.get_invite_preview(invite_code)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{trip_id}", response_model=GroupTripDetail)
def get_trip(
    trip_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = GroupTripService(db)
    try:
        trip = service.get_trip(trip_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Private trips: members only
    if trip.visibility == "private" and not service.is_member(trip_id, uuid.UUID(user_id)):
        raise HTTPException(status_code=403, detail="You must be a member to view this private trip")

    return service.get_trip_detail(trip_id)


@router.put("/{trip_id}", response_model=GroupTripDetail)
def update_trip(
    trip_id: uuid.UUID,
    payload: GroupTripUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = GroupTripService(db)
    try:
        service.update_trip(trip_id, uuid.UUID(user_id), payload)
        return service.get_trip_detail(trip_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/join/{invite_code}", response_model=GroupTripDetail)
def join_trip(
    invite_code: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = GroupTripService(db)
    try:
        trip = service.join_trip(invite_code, uuid.UUID(user_id))
        return service.get_trip_detail(trip.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{trip_id}/leave")
def leave_trip(
    trip_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = GroupTripService(db)
    try:
        service.leave_trip(trip_id, uuid.UUID(user_id))
        return {"detail": "Left the trip"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{trip_id}")
def delete_trip(
    trip_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = GroupTripService(db)
    try:
        service.delete_trip(trip_id, uuid.UUID(user_id))
        return {"detail": "Trip deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/{trip_id}/itinerary")
def get_trip_itinerary(
    trip_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = GroupTripService(db)
    from app.services.itinerary_service import ItineraryService
    it_service = ItineraryService(db)
    
    if not service.is_member(trip_id, uuid.UUID(user_id)):
        raise HTTPException(status_code=403, detail="Must be a member to view itinerary")
        
    # Find itinerary where group_trip_id == trip_id
    from app.models.itinerary import Itinerary
    from sqlalchemy.orm import selectinload
    
    itinerary = db.query(Itinerary).options(selectinload(Itinerary.activities)).filter(Itinerary.group_trip_id == trip_id).first()
    if not itinerary:
        # 404 because no collaborative itinerary created yet
        raise HTTPException(status_code=404, detail="No collaborative itinerary exists for this trip")
        
    return itinerary


@router.post("/{trip_id}/itinerary")
def create_trip_itinerary(
    trip_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Creates a blank collaborative itinerary for the trip"""
    service = GroupTripService(db)
    
    if not service.is_member(trip_id, uuid.UUID(user_id)):
        raise HTTPException(status_code=403, detail="Must be a member to create itinerary")
        
    from app.models.itinerary import Itinerary
    from sqlalchemy.orm import selectinload
    
    existing = db.query(Itinerary).filter(Itinerary.group_trip_id == trip_id).first()
    if existing:
        return existing
        
    trip = service.get_trip(trip_id)
        
    itinerary = Itinerary(
        user_id=uuid.UUID(user_id),  # creator
        group_trip_id=trip_id,
        destination=trip.destination,
        duration_days=(trip.end_date - trip.start_date).days + 1,
        budget=0.0,
        travel_style="medium",
        group_type=trip.visibility,
    )
    db.add(itinerary)
    db.commit()
    db.refresh(itinerary)
    
    # Notify other members
    from app.models.notification import Notification
    from app.models.group_trip import GroupTripMember
    
    members = db.query(GroupTripMember).filter(GroupTripMember.trip_id == trip_id).all()
    for member in members:
        if member.user_id != uuid.UUID(user_id):
            notif = Notification(
                user_id=member.user_id,
                type="itinerary_created",
                message=f"A collaborative itinerary was started for '{trip.title}'.",
                resource_id=trip_id,
                resource_type="trip"
            )
            db.add(notif)
    db.commit()
    
    return db.query(Itinerary).options(selectinload(Itinerary.activities)).filter(Itinerary.id == itinerary.id).first()
