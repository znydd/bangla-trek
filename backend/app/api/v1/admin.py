import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin_user, get_current_moderator_or_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.moderation import (
    ModerationActionRead,
    ModerationApproveRequest,
    ModerationMergeRequest,
    ModerationRejectRequest,
    ModerationRequestChangesRequest,
    PendingSubmissionRead,
)
from app.schemas.place import PlaceDetailRead
from app.services.moderation_service import ModerationService
from app.services.place_service import PlaceService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/place-submissions", response_model=List[PendingSubmissionRead])
async def list_pending_submissions(
    admin: User = Depends(get_current_moderator_or_admin),
    db: Session = Depends(get_db),
):
    """Admin API: List all place contributions in 'pending' status."""
    mod_svc = ModerationService(db)
    return mod_svc.list_pending_submissions()


@router.post("/place-submissions/{place_id}/approve", response_model=PlaceDetailRead)
async def approve_submission(
    place_id: uuid.UUID,
    req: ModerationApproveRequest = ModerationApproveRequest(),
    admin: User = Depends(get_current_moderator_or_admin),
    db: Session = Depends(get_db),
):
    """Admin API: Approve a place submission and publish its initial review."""
    mod_svc = ModerationService(db)
    place = mod_svc.approve_place_submission(
        place_id=place_id, admin_id=admin.id, notes=req.notes
    )
    place_svc = PlaceService(db)
    return place_svc.format_place_detail(place)


@router.post("/place-submissions/{place_id}/reject", response_model=PlaceDetailRead)
async def reject_submission(
    place_id: uuid.UUID,
    req: ModerationRejectRequest,
    admin: User = Depends(get_current_moderator_or_admin),
    db: Session = Depends(get_db),
):
    """Admin API: Reject a place submission with reason."""
    mod_svc = ModerationService(db)
    place = mod_svc.reject_place_submission(
        place_id=place_id, admin_id=admin.id, reason=req.reason
    )
    place_svc = PlaceService(db)
    return place_svc.format_place_detail(place)


@router.post("/place-submissions/{place_id}/request-changes", response_model=PlaceDetailRead)
async def request_changes_submission(
    place_id: uuid.UUID,
    req: ModerationRequestChangesRequest,
    admin: User = Depends(get_current_moderator_or_admin),
    db: Session = Depends(get_db),
):
    """Admin API: Request changes on a place submission."""
    mod_svc = ModerationService(db)
    place = mod_svc.request_changes_place_submission(
        place_id=place_id, admin_id=admin.id, reason=req.reason
    )
    place_svc = PlaceService(db)
    return place_svc.format_place_detail(place)


@router.post("/place-submissions/{place_id}/merge", response_model=PlaceDetailRead)
async def merge_submission(
    place_id: uuid.UUID,
    req: ModerationMergeRequest,
    admin: User = Depends(get_current_moderator_or_admin),
    db: Session = Depends(get_db),
):
    """Admin API: Merge contribution into an existing canonical place."""
    mod_svc = ModerationService(db)
    place = mod_svc.merge_place_submission(
        place_id=place_id,
        admin_id=admin.id,
        target_canonical_place_id=req.target_canonical_place_id,
        reason=req.reason,
    )
    place_svc = PlaceService(db)
    return place_svc.format_place_detail(place)


@router.post("/reviews/{review_id}/hide")
async def hide_review(
    review_id: uuid.UUID,
    reason: str = Query(..., min_length=3),
    admin: User = Depends(get_current_moderator_or_admin),
    db: Session = Depends(get_db),
):
    """Admin API: Hide a policy-violating review."""
    mod_svc = ModerationService(db)
    mod_svc.hide_review(review_id=review_id, admin_id=admin.id, reason=reason)
    return {"message": "Review hidden successfully"}


@router.post("/reviews/{review_id}/restore")
async def restore_review(
    review_id: uuid.UUID,
    admin: User = Depends(get_current_moderator_or_admin),
    db: Session = Depends(get_db),
):
    """Admin API: Restore a hidden review."""
    mod_svc = ModerationService(db)
    mod_svc.restore_review(review_id=review_id, admin_id=admin.id)
    return {"message": "Review restored successfully"}


@router.get("/moderation-logs", response_model=List[ModerationActionRead])
async def list_moderation_logs(
    entity_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    admin: User = Depends(get_current_moderator_or_admin),
    db: Session = Depends(get_db),
):
    """Admin API: Fetch permanent moderation audit trail logs."""
    mod_svc = ModerationService(db)
    return mod_svc.list_moderation_logs(entity_type=entity_type, limit=limit)
