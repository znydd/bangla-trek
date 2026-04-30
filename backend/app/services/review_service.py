import uuid
from typing import List, Optional, Tuple

from sqlalchemy import desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.community_entry import CommunityEntry
from app.models.entry_review import EntryReview
from app.models.entry_review_photo import EntryReviewPhoto
from app.models.itinerary import Itinerary, ItineraryActivity
from app.models.user import User
from app.schemas.review import EntryReviewCreate, EntryReviewUpdate
from app.services.cloudinary_service import CloudinaryService


class ReviewService:
    def __init__(self, db: Session):
        self.db = db

    def _ensure_entry_exists(self, entry_id: uuid.UUID) -> CommunityEntry:
        entry = self.db.get(CommunityEntry, entry_id)
        if not entry:
            raise ValueError("Entry not found")
        return entry

    def _get_review(self, entry_id: uuid.UUID, review_id: uuid.UUID) -> EntryReview:
        stmt = (
            select(EntryReview)
            .where(EntryReview.id == review_id, EntryReview.entry_id == entry_id)
            .options(selectinload(EntryReview.photos))
        )
        review = self.db.execute(stmt).scalar_one_or_none()
        if not review:
            raise ValueError("Review not found")
        return review

    def _attach_author(self, reviews: List[EntryReview]) -> None:
        for review in reviews:
            review.author_name = review.user.name
            review.author_picture_url = review.user.picture_url

    def _validate_trip_context(
        self,
        user_id: uuid.UUID,
        entry_id: uuid.UUID,
        itinerary_id: Optional[uuid.UUID],
        activity_id: Optional[uuid.UUID],
    ) -> None:
        if not itinerary_id and not activity_id:
            return

        itinerary = None
        if itinerary_id:
            itinerary = self.db.get(Itinerary, itinerary_id)
            if not itinerary or itinerary.user_id != user_id:
                raise PermissionError("Not authorized to review with this itinerary")

        if activity_id:
            activity = self.db.get(ItineraryActivity, activity_id)
            if not activity:
                raise ValueError("Itinerary activity not found")

            activity_itinerary = itinerary or self.db.get(
                Itinerary, activity.itinerary_id
            )
            if not activity_itinerary or activity_itinerary.user_id != user_id:
                raise PermissionError("Not authorized to review with this activity")

            if itinerary_id and activity.itinerary_id != itinerary_id:
                raise ValueError("Activity does not belong to this itinerary")

            if activity.community_entry_id and activity.community_entry_id != entry_id:
                raise ValueError("Activity does not match this community entry")

    def list_reviews(
        self,
        entry_id: uuid.UUID,
        user_id: uuid.UUID,
        page: int = 1,
        per_page: int = 6,
        travel_style: Optional[str] = None,
        sort_by: str = "newest",
    ) -> Tuple[List[EntryReview], int, dict, Optional[uuid.UUID]]:
        self._ensure_entry_exists(entry_id)

        query = (
            select(EntryReview)
            .join(User, EntryReview.user_id == User.id)
            .where(EntryReview.entry_id == entry_id)
            .options(selectinload(EntryReview.photos))
        )

        if travel_style:
            query = query.where(EntryReview.travel_style == travel_style)

        if sort_by == "highest_rating":
            query = query.order_by(
                desc(EntryReview.rating), desc(EntryReview.created_at)
            )
        elif sort_by == "lowest_rating":
            query = query.order_by(EntryReview.rating, desc(EntryReview.created_at))
        else:
            query = query.order_by(desc(EntryReview.created_at))

        total_stmt = select(func.count()).select_from(query.subquery())
        total = self.db.execute(total_stmt).scalar() or 0

        items = list(
            self.db.execute(
                query.offset((page - 1) * per_page).limit(per_page)
            ).scalars().all()
        )
        self._attach_author(items)

        summary = self.get_summary(entry_id)
        my_review_id = self.db.execute(
            select(EntryReview.id).where(
                EntryReview.entry_id == entry_id,
                EntryReview.user_id == user_id,
            )
        ).scalar_one_or_none()

        return items, total, summary, my_review_id

    def get_summary(self, entry_id: uuid.UUID) -> dict:
        rows = self.db.execute(
            select(EntryReview.rating, EntryReview.travel_style).where(
                EntryReview.entry_id == entry_id
            )
        ).all()

        breakdown = {i: 0 for i in range(1, 6)}
        style_counts: dict[str, int] = {}

        for rating, travel_style in rows:
            breakdown[rating] += 1
            style_counts[travel_style] = style_counts.get(travel_style, 0) + 1

        review_count = len(rows)
        average_rating = (
            round(sum(rating for rating, _ in rows) / review_count, 1)
            if review_count
            else None
        )

        return {
            "average_rating": average_rating,
            "review_count": review_count,
            "breakdown": breakdown,
            "by_travel_style": [
                {"travel_style": style, "count": count}
                for style, count in sorted(style_counts.items())
            ],
        }

    def create_review(
        self,
        entry_id: uuid.UUID,
        user_id: uuid.UUID,
        payload: EntryReviewCreate,
    ) -> EntryReview:
        self._ensure_entry_exists(entry_id)
        self._validate_trip_context(
            user_id, entry_id, payload.itinerary_id, payload.activity_id
        )

        review = EntryReview(
            entry_id=entry_id,
            user_id=user_id,
            **payload.model_dump(),
        )
        self.db.add(review)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ValueError("You have already reviewed this entry")

        self.db.refresh(review)
        return self.get_review_for_read(entry_id, review.id)

    def update_review(
        self,
        entry_id: uuid.UUID,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
        payload: EntryReviewUpdate,
    ) -> EntryReview:
        review = self._get_review(entry_id, review_id)
        if review.user_id != user_id:
            raise PermissionError("Not authorized to update this review")

        data = payload.model_dump(exclude_unset=True)
        self._validate_trip_context(
            user_id,
            entry_id,
            data.get("itinerary_id", review.itinerary_id),
            data.get("activity_id", review.activity_id),
        )

        for key, value in data.items():
            setattr(review, key, value)

        self.db.commit()
        self.db.refresh(review)
        return self.get_review_for_read(entry_id, review_id)

    def delete_review(
        self,
        entry_id: uuid.UUID,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        review = self._get_review(entry_id, review_id)
        if review.user_id != user_id:
            raise PermissionError("Not authorized to delete this review")

        for photo in review.photos:
            CloudinaryService.delete_image(photo.public_id)

        self.db.delete(review)
        self.db.commit()

    def get_review_for_read(
        self,
        entry_id: uuid.UUID,
        review_id: uuid.UUID,
    ) -> EntryReview:
        review = self._get_review(entry_id, review_id)
        review.author_name = review.user.name
        review.author_picture_url = review.user.picture_url
        return review

    def add_photo(
        self,
        entry_id: uuid.UUID,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
        url: str,
        public_id: str,
    ) -> EntryReview:
        review = self._get_review(entry_id, review_id)
        if review.user_id != user_id:
            raise PermissionError("Not authorized to add photos to this review")

        self.db.add(EntryReviewPhoto(review_id=review_id, url=url, public_id=public_id))
        self.db.commit()
        return self.get_review_for_read(entry_id, review_id)

    def delete_photo(
        self,
        entry_id: uuid.UUID,
        review_id: uuid.UUID,
        photo_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> EntryReview:
        review = self._get_review(entry_id, review_id)
        if review.user_id != user_id:
            raise PermissionError("Not authorized to delete photos from this review")

        photo = self.db.execute(
            select(EntryReviewPhoto).where(
                EntryReviewPhoto.id == photo_id,
                EntryReviewPhoto.review_id == review_id,
            )
        ).scalar_one_or_none()
        if not photo:
            raise ValueError("Photo not found")

        CloudinaryService.delete_image(photo.public_id)
        self.db.delete(photo)
        self.db.commit()
        return self.get_review_for_read(entry_id, review_id)
