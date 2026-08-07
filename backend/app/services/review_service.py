import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.review import (
    Review,
    ReviewHelpfulVote,
    ReviewMedia,
    ReviewPaymentMethod,
)
from app.models.user import User
from app.schemas.review import (
    CostRange,
    DistributionOption,
    MetricDistribution,
    ReviewCreate,
    ReviewMediaRead,
    ReviewRead,
    ReviewSummaryRead,
    ReviewUpdate,
    ReviewUserRead,
)


class ReviewService:
    def __init__(self, db: Session):
        self.db = db

    def create_review(
        self, place_id: uuid.UUID, user_id: uuid.UUID, review_in: ReviewCreate
    ) -> ReviewRead:
        """Create a new review for a place."""
        # Check existing review for same user, place, and visited_on date
        existing = (
            self.db.query(Review)
            .filter(
                Review.place_id == place_id,
                Review.user_id == user_id,
                Review.visited_on == review_in.visited_on,
                Review.deleted_at.is_(None),
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="You have already submitted a review for this place for the selected visit date.",
            )

        review = Review(
            place_id=place_id,
            user_id=user_id,
            status="published",
            rating=review_in.rating,
            visited_on=review_in.visited_on,
            travel_style=review_in.travel_style,
            group_type=review_in.group_type,
            group_size=review_in.group_size,
            starting_location=review_in.starting_location,
            actual_cost_bdt=review_in.actual_cost_bdt,
            title=review_in.title,
            travel_guide=review_in.travel_guide,
            crowd_level=review_in.crowd_level,
            access_difficulty=review_in.access_difficulty,
            road_condition=review_in.road_condition,
            safety=review_in.safety,
            cleanliness=review_in.cleanliness,
            mobile_carrier=review_in.mobile_carrier,
            strongest_network=review_in.strongest_network,
            network_reliability=review_in.network_reliability,
        )
        self.db.add(review)
        self.db.flush()

        # Add payment methods
        if review_in.payment_methods:
            for pm in set(review_in.payment_methods):
                self.db.add(
                    ReviewPaymentMethod(review_id=review.id, payment_method=pm)
                )

        # Add media
        if review_in.media:
            for m in review_in.media:
                self.db.add(
                    ReviewMedia(
                        review_id=review.id,
                        media_type=m.media_type,
                        url=m.url,
                        storage_public_id=m.storage_public_id,
                        platform=m.platform,
                        caption=m.caption,
                        sort_order=m.sort_order,
                        moderation_status="published",
                    )
                )

        self.db.commit()
        self.db.refresh(review)
        return self._format_review_read(review, current_user_id=user_id)

    def update_review(
        self, review_id: uuid.UUID, user_id: uuid.UUID, update_in: ReviewUpdate
    ) -> ReviewRead:
        """Update an existing review owned by the user."""
        review = (
            self.db.query(Review)
            .filter(
                Review.id == review_id,
                Review.user_id == user_id,
                Review.deleted_at.is_(None),
            )
            .first()
        )
        if not review:
            raise HTTPException(status_code=404, detail="Review not found or unauthorized")

        update_data = update_in.model_dump(exclude_unset=True)
        payment_methods = update_data.pop("payment_methods", None)

        for field, val in update_data.items():
            setattr(review, field, val)

        if payment_methods is not None:
            self.db.query(ReviewPaymentMethod).filter(
                ReviewPaymentMethod.review_id == review.id
            ).delete()
            for pm in set(payment_methods):
                self.db.add(
                    ReviewPaymentMethod(review_id=review.id, payment_method=pm)
                )

        self.db.commit()
        self.db.refresh(review)
        return self._format_review_read(review, current_user_id=user_id)

    def soft_delete_review(self, review_id: uuid.UUID, user_id: uuid.UUID):
        """Soft delete a review owned by the user."""
        review = (
            self.db.query(Review)
            .filter(
                Review.id == review_id,
                Review.user_id == user_id,
                Review.deleted_at.is_(None),
            )
            .first()
        )
        if not review:
            raise HTTPException(status_code=404, detail="Review not found or unauthorized")

        review.deleted_at = datetime.now(timezone.utc)
        review.status = "removed"
        self.db.commit()

    def toggle_helpful_vote(
        self, review_id: uuid.UUID, user_id: uuid.UUID
    ) -> dict:
        """Toggle helpful vote on a review."""
        review = (
            self.db.query(Review)
            .filter(
                Review.id == review_id,
                Review.status == "published",
                Review.deleted_at.is_(None),
            )
            .first()
        )
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")

        vote = (
            self.db.query(ReviewHelpfulVote)
            .filter(
                ReviewHelpfulVote.review_id == review_id,
                ReviewHelpfulVote.user_id == user_id,
            )
            .first()
        )

        if vote:
            self.db.delete(vote)
            review.helpful_count = max(0, review.helpful_count - 1)
            is_helpful = False
        else:
            self.db.add(ReviewHelpfulVote(review_id=review_id, user_id=user_id))
            review.helpful_count += 1
            is_helpful = True

        self.db.commit()
        return {"helpful_count": review.helpful_count, "is_helpful_by_me": is_helpful}

    def list_reviews_for_place(
        self,
        place_id: uuid.UUID,
        current_user_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[ReviewRead]:
        """Fetch published reviews for a place."""
        reviews = (
            self.db.query(Review)
            .options(
                joinedload(Review.user),
                joinedload(Review.payment_methods),
                joinedload(Review.media),
            )
            .filter(
                Review.place_id == place_id,
                Review.status == "published",
                Review.deleted_at.is_(None),
            )
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return [self._format_review_read(r, current_user_id) for r in reviews]

    def get_review_summary(self, place_id: uuid.UUID) -> ReviewSummaryRead:
        """Calculate SQL aggregated metric distributions for a place."""
        published_reviews_q = self.db.query(Review).filter(
            Review.place_id == place_id,
            Review.status == "published",
            Review.deleted_at.is_(None),
        )

        total_reviews = published_reviews_q.count()
        if total_reviews == 0:
            empty_dist = MetricDistribution(total=0, options=[])
            return ReviewSummaryRead(
                place_id=place_id,
                total_reviews=0,
                average_rating=0.0,
                most_recent_visit=None,
                most_common_travel_style=None,
                average_group_size=None,
                typical_access_difficulty=None,
                most_reported_payment_method=None,
                cost_range=CostRange(),
                rating_breakdown=empty_dist,
                crowd_level=empty_dist,
                access_difficulty=empty_dist,
                road_condition=empty_dist,
                safety=empty_dist,
                cleanliness=empty_dist,
                mobile_carrier=empty_dist,
                network_reliability=empty_dist,
                payment_methods=empty_dist,
            )

        # Average rating & most recent visit date
        agg_stats = (
            self.db.query(
                func.avg(Review.rating).label("avg_rating"),
                func.max(Review.visited_on).label("max_visit"),
                func.avg(Review.group_size).label("avg_group_size"),
                func.min(Review.actual_cost_bdt).label("min_cost"),
                func.max(Review.actual_cost_bdt).label("max_cost"),
            )
            .filter(
                Review.place_id == place_id,
                Review.status == "published",
                Review.deleted_at.is_(None),
            )
            .first()
        )

        avg_rating = round(float(agg_stats.avg_rating), 1) if agg_stats.avg_rating else 0.0
        most_recent_visit = agg_stats.max_visit
        avg_group_size = round(float(agg_stats.avg_group_size), 1) if agg_stats.avg_group_size else None
        min_cost = float(agg_stats.min_cost) if agg_stats.min_cost is not None else None
        max_cost = float(agg_stats.max_cost) if agg_stats.max_cost is not None else None

        # Median cost calculation via SQL
        costs = (
            self.db.query(Review.actual_cost_bdt)
            .filter(
                Review.place_id == place_id,
                Review.status == "published",
                Review.deleted_at.is_(None),
                Review.actual_cost_bdt.is_not(None),
            )
            .all()
        )
        cost_vals = sorted([float(c[0]) for c in costs])
        median_cost = None
        if cost_vals:
            n = len(cost_vals)
            mid = n // 2
            median_cost = cost_vals[mid] if n % 2 != 0 else (cost_vals[mid - 1] + cost_vals[mid]) / 2.0

        # Helper to compute metric distributions
        def _get_metric_dist(column_attr) -> MetricDistribution:
            rows = (
                self.db.query(column_attr, func.count(Review.id))
                .filter(
                    Review.place_id == place_id,
                    Review.status == "published",
                    Review.deleted_at.is_(None),
                    column_attr.is_not(None),
                )
                .group_by(column_attr)
                .order_by(func.count(Review.id).desc())
                .all()
            )
            metric_total = sum(r[1] for r in rows)
            options = [
                DistributionOption(
                    value=str(r[0]),
                    count=r[1],
                    percentage=round((r[1] / metric_total) * 100.0, 1) if metric_total > 0 else 0.0,
                )
                for r in rows
            ]
            return MetricDistribution(total=metric_total, options=options)

        # Rating breakdown (1-5 stars)
        rating_rows = (
            self.db.query(Review.rating, func.count(Review.id))
            .filter(
                Review.place_id == place_id,
                Review.status == "published",
                Review.deleted_at.is_(None),
            )
            .group_by(Review.rating)
            .all()
        )
        rating_counts = {r[0]: r[1] for r in rating_rows}
        rating_options = [
            DistributionOption(
                value=f"{star} Stars",
                count=rating_counts.get(star, 0),
                percentage=round((rating_counts.get(star, 0) / total_reviews) * 100.0, 1),
            )
            for star in range(5, 0, -1)
        ]
        rating_dist = MetricDistribution(total=total_reviews, options=rating_options)

        # Payment methods breakdown
        pm_rows = (
            self.db.query(
                ReviewPaymentMethod.payment_method, func.count(ReviewPaymentMethod.id)
            )
            .join(Review, Review.id == ReviewPaymentMethod.review_id)
            .filter(
                Review.place_id == place_id,
                Review.status == "published",
                Review.deleted_at.is_(None),
            )
            .group_by(ReviewPaymentMethod.payment_method)
            .order_by(func.count(ReviewPaymentMethod.id).desc())
            .all()
        )
        pm_total = sum(r[1] for r in pm_rows)
        pm_options = [
            DistributionOption(
                value=r[0],
                count=r[1],
                percentage=round((r[1] / pm_total) * 100.0, 1) if pm_total > 0 else 0.0,
            )
            for r in pm_rows
        ]
        pm_dist = MetricDistribution(total=pm_total, options=pm_options)

        # Compute metric distributions
        crowd_dist = _get_metric_dist(Review.crowd_level)
        access_dist = _get_metric_dist(Review.access_difficulty)
        road_dist = _get_metric_dist(Review.road_condition)
        safety_dist = _get_metric_dist(Review.safety)
        cleanliness_dist = _get_metric_dist(Review.cleanliness)
        carrier_dist = _get_metric_dist(Review.mobile_carrier)
        network_dist = _get_metric_dist(Review.network_reliability)
        travel_style_dist = _get_metric_dist(Review.travel_style)

        most_common_travel_style = travel_style_dist.options[0].value if travel_style_dist.options else None
        typical_access_difficulty = access_dist.options[0].value if access_dist.options else None
        most_reported_pm = pm_dist.options[0].value if pm_dist.options else None

        return ReviewSummaryRead(
            place_id=place_id,
            total_reviews=total_reviews,
            average_rating=avg_rating,
            most_recent_visit=most_recent_visit,
            most_common_travel_style=most_common_travel_style,
            average_group_size=avg_group_size,
            typical_access_difficulty=typical_access_difficulty,
            most_reported_payment_method=most_reported_pm,
            cost_range=CostRange(min=min_cost, max=max_cost, median=median_cost),
            rating_breakdown=rating_dist,
            crowd_level=crowd_dist,
            access_difficulty=access_dist,
            road_condition=road_dist,
            safety=safety_dist,
            cleanliness=cleanliness_dist,
            mobile_carrier=carrier_dist,
            network_reliability=network_dist,
            payment_methods=pm_dist,
        )

    def _format_review_read(
        self, review: Review, current_user_id: Optional[uuid.UUID] = None
    ) -> ReviewRead:
        user_read = ReviewUserRead(
            id=review.user.id,
            name=review.user.name,
            picture_url=review.user.picture_url,
        )

        is_helpful = False
        if current_user_id:
            is_helpful = (
                self.db.query(ReviewHelpfulVote)
                .filter(
                    ReviewHelpfulVote.review_id == review.id,
                    ReviewHelpfulVote.user_id == current_user_id,
                )
                .first()
                is not None
            )

        pms = [pm.payment_method for pm in review.payment_methods]
        media_items = [
            ReviewMediaRead.model_validate(m)
            for m in sorted(review.media, key=lambda x: x.sort_order)
            if m.moderation_status == "published"
        ]

        return ReviewRead(
            id=review.id,
            place_id=review.place_id,
            user_id=review.user_id,
            user=user_read,
            status=review.status,
            rating=review.rating,
            visited_on=review.visited_on,
            travel_style=review.travel_style,
            group_type=review.group_type,
            group_size=review.group_size,
            starting_location=review.starting_location,
            actual_cost_bdt=float(review.actual_cost_bdt) if review.actual_cost_bdt is not None else None,
            title=review.title,
            travel_guide=review.travel_guide,
            crowd_level=review.crowd_level,
            access_difficulty=review.access_difficulty,
            road_condition=review.road_condition,
            safety=review.safety,
            cleanliness=review.cleanliness,
            mobile_carrier=review.mobile_carrier,
            strongest_network=review.strongest_network,
            network_reliability=review.network_reliability,
            helpful_count=review.helpful_count,
            is_helpful_by_me=is_helpful,
            payment_methods=pms,
            media=media_items,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )
