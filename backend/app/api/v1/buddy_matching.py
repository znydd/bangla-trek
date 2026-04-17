import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.buddy_match import (
    BuddyDiscoveryFilters,
    BuddyMatchAction,
    BuddyMatchList,
    BuddyMatchRead,
    BuddyMatchSuggestion,
)
from app.services.buddy_matching_service import BuddyMatchingService

router = APIRouter(prefix="/buddy-matching", tags=["buddy-matching"])


@router.get("/discover", response_model=List[BuddyMatchSuggestion])
def discover_buddies(
    destination: Optional[str] = Query(None, description="Filter by destination"),
    interest: Optional[str] = Query(None, description="Filter by interest"),
    min_match_score: float = Query(0.1, ge=0.0, le=1.0),
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Discover potential travel buddies based on:
    - Overlapping interests from itineraries
    - Overlapping destinations from itineraries and group trips
    - Shared group trip memberships
    """
    service = BuddyMatchingService(db)

    filters = BuddyDiscoveryFilters(
        destination=destination,
        interest=interest,
        min_match_score=min_match_score,
        limit=limit,
    )

    suggestions = service.discover_buddies(uuid.UUID(user_id), filters)

    # Auto-save suggestions to database
    for suggestion in suggestions:
        service.save_match(uuid.UUID(user_id), suggestion, status="suggested")

    return suggestions


@router.get("/my-matches", response_model=BuddyMatchList)
def list_my_matches(
    status: Optional[str] = Query(
        None, pattern="^(suggested|pending|accepted|rejected|blocked)$"
    ),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get my buddy matches with optional status filter."""
    service = BuddyMatchingService(db)

    items, total = service.get_my_matches(
        uuid.UUID(user_id), status=status, page=page, per_page=per_page
    )

    total_pages = (total + per_page - 1) // per_page

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


@router.get("/incoming-requests", response_model=BuddyMatchList)
def list_incoming_requests(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get pending connection requests from other users who want to connect with me.
    These are matches where I'm the matched_user_id and status is 'pending'.
    """
    service = BuddyMatchingService(db)

    items, total = service.get_incoming_requests(
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


@router.post("/matches/{match_id}/action", response_model=BuddyMatchRead)
def match_action(
    match_id: uuid.UUID,
    payload: BuddyMatchAction,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Accept, reject, or block a buddy match."""
    service = BuddyMatchingService(db)

    try:
        match = service.update_match_status(
            match_id, uuid.UUID(user_id), payload.action
        )

        # Get matched user info for response
        from app.models.user import User

        matched_user = (
            db.execute(select(User).where(User.id == match.matched_user_id))
            .scalar_one()
        )

        return {
            "id": match.id,
            "user_id": match.user_id,
            "matched_user_id": match.matched_user_id,
            "matched_user_name": matched_user.name,
            "matched_user_picture_url": matched_user.picture_url,
            "match_score": match.match_score,
            "common_interests": match.common_interests,
            "common_destinations": match.common_destinations,
            "status": match.status,
            "created_at": match.created_at,
            "updated_at": match.updated_at,
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/matches/{match_id}")
def delete_match(
    match_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Delete a buddy match."""
    service = BuddyMatchingService(db)

    try:
        service.delete_match(match_id, uuid.UUID(user_id))
        return {"detail": "Match deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/connect/{user_id}")
def connect_with_user(
    user_id: uuid.UUID,
    user_id_from_token: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Initiate a connection with a specific user (by user_id).
    Creates a match record with 'pending' status.
    """
    from app.models.user import User
    from app.services.buddy_matching_service import BuddyMatchingService

    # Check if user exists
    target_user = (
        db.execute(select(User).where(User.id == user_id))
        .scalar_one_or_none()
    )

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if str(user_id) == user_id_from_token:
        raise HTTPException(status_code=400, detail="Cannot connect with yourself")

    service = BuddyMatchingService(db)

    # Create a match suggestion manually
    from app.schemas.buddy_match import BuddyMatchSuggestion

    suggestion = BuddyMatchSuggestion(
        matched_user_id=user_id,
        matched_user_name=target_user.name,
        matched_user_picture_url=target_user.picture_url,
        match_score=0.0,  # Manual connection
        common_interests=[],
        common_destinations=[],
        match_source="manual",
    )

    match = service.save_match(
        uuid.UUID(user_id_from_token), suggestion, status="pending"
    )
    match.initiated_by = uuid.UUID(user_id_from_token)
    db.commit()

    return {
        "detail": "Connection request sent",
        "match_id": match.id,
        "status": match.status,
    }
