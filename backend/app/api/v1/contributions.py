import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.contribution import (
    DuplicateCheckResponse,
    PlaceDraftCreate,
    PlaceDraftUpdate,
    PlaceSubmissionSubmit,
    UserContributionRead,
)
from app.schemas.place import PlaceDetailRead
from app.services.contribution_service import ContributionService
from app.services.place_service import PlaceService

router = APIRouter(tags=["contributions"])


@router.get("/places/duplicate-check", response_model=DuplicateCheckResponse)
async def check_duplicate_place(
    name: str = Query(..., min_length=2, description="Place name to check for duplicates"),
    district: Optional[str] = Query(None),
    upazila: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Protected/Public API: Check existing approved or pending places to avoid duplicate submissions."""
    contrib_svc = ContributionService(db)
    return contrib_svc.duplicate_check(name=name, district=district, upazila=upazila)


@router.post("/places/drafts", response_model=PlaceDetailRead)
async def create_place_draft(
    draft_in: PlaceDraftCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: Create a new place submission draft."""
    contrib_svc = ContributionService(db)
    place = contrib_svc.create_draft_place(user_id=current_user.id, draft_in=draft_in)
    place_svc = PlaceService(db)
    return place_svc.format_place_detail(place)


@router.patch("/places/drafts/{place_id}", response_model=PlaceDetailRead)
async def update_place_draft(
    place_id: uuid.UUID,
    update_in: PlaceDraftUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: Update an existing draft or requested-changes place submission."""
    contrib_svc = ContributionService(db)
    place = contrib_svc.update_draft_place(
        place_id=place_id, user_id=current_user.id, update_in=update_in
    )
    place_svc = PlaceService(db)
    return place_svc.format_place_detail(place)


@router.post("/places/drafts/{place_id}/submit", response_model=PlaceDetailRead)
async def submit_place_draft(
    place_id: uuid.UUID,
    submit_in: PlaceSubmissionSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: Submit draft place and optional initial review to admin queue."""
    contrib_svc = ContributionService(db)
    place = contrib_svc.submit_place_contribution(
        place_id=place_id, user_id=current_user.id, submit_in=submit_in
    )
    place_svc = PlaceService(db)
    return place_svc.format_place_detail(place)


@router.get("/me/place-contributions", response_model=List[UserContributionRead])
async def list_my_contributions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: List all place contributions submitted by the logged-in user."""
    contrib_svc = ContributionService(db)
    return contrib_svc.list_user_contributions(user_id=current_user.id)
