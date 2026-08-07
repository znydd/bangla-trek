import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_optional_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.place import PlaceCardRead, PlaceDetailRead
from app.schemas.review import (
    ReviewCreate,
    ReviewRead,
    ReviewSummaryRead,
    ReviewUpdate,
)
from app.services.place_service import PlaceService
from app.services.review_service import ReviewService

router = APIRouter(prefix="/places", tags=["places"])


@router.get("", response_model=List[PlaceCardRead])
async def list_places(
    category: Optional[str] = Query(None, description="Filter by place category"),
    district: Optional[str] = Query(None, description="Filter by district"),
    q: Optional[str] = Query(None, description="Search query for name, alias, location"),
    query: Optional[str] = Query(None, description="Search query fallback"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Public API: List approved places with search and filter parameters."""
    search_q = q or query
    place_service = PlaceService(db)
    return place_service.list_approved_places(
        category=category,
        district=district,
        query=search_q,
        skip=skip,
        limit=limit,
    )


@router.get("/{slug}", response_model=PlaceDetailRead)
async def get_place_by_slug(slug: str, db: Session = Depends(get_db)):
    """Public API: Retrieve detailed information for an approved place by slug."""
    place_service = PlaceService(db)
    place = place_service.get_approved_place_by_slug(slug)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place


@router.get("/{place_id}/reviews", response_model=List[ReviewRead])
async def list_place_reviews(
    place_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Public API: List published reviews for a place."""
    place_service = PlaceService(db)
    if not place_service.get_place_by_id(place_id):
        raise HTTPException(status_code=404, detail="Place not found")

    review_service = ReviewService(db)
    current_user_id = current_user.id if current_user else None
    return review_service.list_reviews_for_place(
        place_id=place_id,
        current_user_id=current_user_id,
        skip=skip,
        limit=limit,
    )


@router.get("/{place_id}/review-summary", response_model=ReviewSummaryRead)
async def get_place_review_summary(
    place_id: uuid.UUID, db: Session = Depends(get_db)
):
    """Public API: Get SQL-aggregated review metrics and distributions for a place."""
    place_service = PlaceService(db)
    if not place_service.get_place_by_id(place_id):
        raise HTTPException(status_code=404, detail="Place not found")

    review_service = ReviewService(db)
    return review_service.get_review_summary(place_id)


@router.post("/{place_id}/reviews", response_model=ReviewRead)
async def create_place_review(
    place_id: uuid.UUID,
    review_in: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: Post a review for an approved place."""
    place_service = PlaceService(db)
    place = place_service.get_place_by_id(place_id)
    if not place or place.status != "approved":
        raise HTTPException(status_code=404, detail="Approved place not found")

    review_service = ReviewService(db)
    return review_service.create_review(
        place_id=place_id,
        user_id=current_user.id,
        review_in=review_in,
    )


@router.patch("/{place_id}/reviews/{review_id}", response_model=ReviewRead)
async def update_place_review(
    place_id: uuid.UUID,
    review_id: uuid.UUID,
    update_in: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: Update own review for a place."""
    review_service = ReviewService(db)
    return review_service.update_review(
        review_id=review_id,
        user_id=current_user.id,
        update_in=update_in,
    )


@router.delete("/{place_id}/reviews/{review_id}")
async def delete_place_review(
    place_id: uuid.UUID,
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: Soft-delete own review for a place."""
    review_service = ReviewService(db)
    review_service.soft_delete_review(review_id=review_id, user_id=current_user.id)
    return {"message": "Review deleted successfully"}


@router.post("/{place_id}/reviews/{review_id}/helpful")
async def toggle_helpful_vote(
    place_id: uuid.UUID,
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: Toggle helpful vote on a review."""
    review_service = ReviewService(db)
    return review_service.toggle_helpful_vote(
        review_id=review_id, user_id=current_user.id
    )
