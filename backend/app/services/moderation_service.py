import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.moderation import ModerationAction
from app.models.place import Place
from app.models.review import Review
from app.models.user import User
from app.schemas.moderation import (
    ModerationActionRead,
    PendingSubmissionRead,
)
from app.services.place_service import PlaceService
from app.services.review_service import ReviewService


class ModerationService:
    def __init__(self, db: Session):
        self.db = db

    def list_pending_submissions(self) -> List[PendingSubmissionRead]:
        """Fetch all place submissions currently in 'pending' status."""
        places = (
            self.db.query(Place)
            .options(
                joinedload(Place.creator),
                joinedload(Place.aliases),
                joinedload(Place.tags),
                joinedload(Place.media),
            )
            .filter(Place.status == "pending")
            .order_by(Place.created_at.asc())
            .all()
        )

        place_svc = PlaceService(self.db)
        review_svc = ReviewService(self.db)

        items = []
        for p in places:
            detail = place_svc.get_approved_place_by_slug(p.slug)
            if not detail:
                # Format detail manually for non-approved place
                detail = place_svc.get_approved_place_by_slug(p.slug) or place_svc.get_place_by_id(p.id)

            # Get initial review
            initial_review = (
                self.db.query(Review)
                .filter(Review.place_id == p.id)
                .order_by(Review.created_at.asc())
                .first()
            )
            initial_review_read = (
                review_svc._format_review_read(initial_review) if initial_review else None
            )

            submitter_name = p.creator.name if p.creator else None
            submitter_email = p.creator.email if p.creator else None

            items.append(
                PendingSubmissionRead(
                    place=place_svc.format_place_detail(p),
                    submitter_name=submitter_name,
                    submitter_email=submitter_email,
                    initial_review=initial_review_read,
                )
            )
        return items


    def approve_place_submission(
        self, place_id: uuid.UUID, admin_id: uuid.UUID, notes: Optional[str] = None
    ) -> Place:
        """Approve place submission and publish initial review in one transaction."""
        place = self.db.query(Place).filter(Place.id == place_id).first()
        if not place or place.status != "pending":
            raise HTTPException(
                status_code=404, detail="Pending place submission not found."
            )

        place.status = "approved"
        place.approved_by = admin_id
        place.approved_at = datetime.now(timezone.utc)

        # Publish initial review if pending
        reviews = self.db.query(Review).filter(Review.place_id == place.id).all()
        for r in reviews:
            if r.status == "pending":
                r.status = "published"

        # Log moderation audit action
        log = ModerationAction(
            entity_type="place",
            entity_id=place.id,
            action="approved",
            performed_by=admin_id,
            reason=notes or "Approved by admin",
        )
        self.db.add(log)

        self.db.commit()
        self.db.refresh(place)
        return place

    def reject_place_submission(
        self, place_id: uuid.UUID, admin_id: uuid.UUID, reason: str
    ) -> Place:
        """Reject place submission with reason."""
        place = self.db.query(Place).filter(Place.id == place_id).first()
        if not place or place.status != "pending":
            raise HTTPException(
                status_code=404, detail="Pending place submission not found."
            )

        place.status = "rejected"

        reviews = self.db.query(Review).filter(Review.place_id == place.id).all()
        for r in reviews:
            r.status = "removed"

        log = ModerationAction(
            entity_type="place",
            entity_id=place.id,
            action="rejected",
            performed_by=admin_id,
            reason=reason,
        )
        self.db.add(log)

        self.db.commit()
        self.db.refresh(place)
        return place

    def request_changes_place_submission(
        self, place_id: uuid.UUID, admin_id: uuid.UUID, reason: str
    ) -> Place:
        """Request changes on place submission from contributor."""
        place = self.db.query(Place).filter(Place.id == place_id).first()
        if not place or place.status != "pending":
            raise HTTPException(
                status_code=404, detail="Pending place submission not found."
            )

        place.status = "changes_requested"

        log = ModerationAction(
            entity_type="place",
            entity_id=place.id,
            action="requested_changes",
            performed_by=admin_id,
            reason=reason,
        )
        self.db.add(log)

        self.db.commit()
        self.db.refresh(place)
        return place

    def merge_place_submission(
        self,
        place_id: uuid.UUID,
        admin_id: uuid.UUID,
        target_canonical_place_id: uuid.UUID,
        reason: str,
    ) -> Place:
        """Merge contribution into existing canonical place and move initial review."""
        submission = self.db.query(Place).filter(Place.id == place_id).first()
        if not submission or submission.status != "pending":
            raise HTTPException(
                status_code=404, detail="Pending place submission not found."
            )

        canonical = (
            self.db.query(Place)
            .filter(Place.id == target_canonical_place_id, Place.status == "approved")
            .first()
        )
        if not canonical:
            raise HTTPException(
                status_code=404, detail="Target canonical approved place not found."
            )

        submission.status = "merged"
        submission.duplicate_of_place_id = canonical.id

        # Re-attribute initial reviews to the canonical place
        reviews = self.db.query(Review).filter(Review.place_id == submission.id).all()
        for r in reviews:
            r.place_id = canonical.id
            r.status = "published"

        log = ModerationAction(
            entity_type="place",
            entity_id=submission.id,
            action="merged",
            performed_by=admin_id,
            reason=reason,
            meta_data={"target_canonical_place_id": str(canonical.id)},
        )
        self.db.add(log)

        self.db.commit()
        self.db.refresh(submission)
        return submission

    def hide_review(
        self, review_id: uuid.UUID, admin_id: uuid.UUID, reason: str
    ):
        """Hide a reported or policy-violating review."""
        review = self.db.query(Review).filter(Review.id == review_id).first()
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")

        review.status = "hidden"
        log = ModerationAction(
            entity_type="review",
            entity_id=review.id,
            action="hidden",
            performed_by=admin_id,
            reason=reason,
        )
        self.db.add(log)
        self.db.commit()

    def restore_review(self, review_id: uuid.UUID, admin_id: uuid.UUID):
        """Restore a hidden review."""
        review = self.db.query(Review).filter(Review.id == review_id).first()
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")

        review.status = "published"
        log = ModerationAction(
            entity_type="review",
            entity_id=review.id,
            action="restored",
            performed_by=admin_id,
            reason="Restored by admin",
        )
        self.db.add(log)
        self.db.commit()

    def list_moderation_logs(
        self, entity_type: Optional[str] = None, limit: int = 50
    ) -> List[ModerationActionRead]:
        """List moderation audit entries."""
        query = (
            self.db.query(ModerationAction)
            .options(joinedload(ModerationAction.performer))
            .order_by(ModerationAction.created_at.desc())
        )
        if entity_type:
            query = query.filter(ModerationAction.entity_type == entity_type)

        logs = query.limit(limit).all()
        return [
            ModerationActionRead(
                id=log.id,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                action=log.action,
                performed_by=log.performed_by,
                performer_name=log.performer.name if log.performer else None,
                reason=log.reason,
                meta_data=log.meta_data,
                created_at=log.created_at,
            )
            for log in logs
        ]
