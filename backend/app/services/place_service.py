import uuid
from typing import List, Optional
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.place import Place, PlaceAlias, PlaceMedia, PlaceTag
from app.models.review import Review
from app.schemas.place import PlaceCardRead, PlaceDetailRead, PlaceMediaRead


class PlaceService:
    def __init__(self, db: Session):
        self.db = db

    def list_approved_places(
        self,
        category: Optional[str] = None,
        district: Optional[str] = None,
        query: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[PlaceCardRead]:
        """Fetch approved places with search filtering and review rating statistics."""
        stmt = (
            select(
                Place,
                func.coalesce(func.avg(Review.rating), 0.0).label("avg_rating"),
                func.count(Review.id).label("review_count"),
            )
            .outerjoin(
                Review,
                (Review.place_id == Place.id)
                & (Review.status == "published")
                & (Review.deleted_at.is_(None)),
            )
            .filter(Place.status == "approved")
            .group_by(Place.id)
        )

        if category:
            stmt = stmt.filter(func.lower(Place.category) == category.lower())

        if district:
            stmt = stmt.filter(func.lower(Place.district) == district.lower())

        if query:
            clean_q = query.strip().lower()
            stmt = stmt.outerjoin(PlaceAlias, PlaceAlias.place_id == Place.id).filter(
                or_(
                    func.lower(Place.name).contains(clean_q),
                    func.lower(Place.normalized_name).contains(clean_q),
                    func.lower(Place.summary).contains(clean_q),
                    func.lower(Place.district).contains(clean_q),
                    func.lower(Place.upazila).contains(clean_q),
                    func.lower(PlaceAlias.normalized_alias).contains(clean_q),
                )
            )

        stmt = stmt.order_by(Place.name.asc()).offset(skip).limit(limit)
        results = self.db.execute(stmt).all()

        cards = []
        for place, avg_rating, review_count in results:
            # Fetch tags
            tags = [
                t.tag
                for t in self.db.query(PlaceTag)
                .filter(PlaceTag.place_id == place.id)
                .all()
            ]

            # Primary image
            primary_media = (
                self.db.query(PlaceMedia)
                .filter(
                    PlaceMedia.place_id == place.id,
                    PlaceMedia.media_type == "photo",
                    PlaceMedia.moderation_status == "approved",
                )
                .order_by(PlaceMedia.sort_order.asc())
                .first()
            )
            primary_image_url = primary_media.url if primary_media else None

            cards.append(
                PlaceCardRead(
                    id=place.id,
                    slug=place.slug,
                    name=place.name,
                    category=place.category,
                    summary=place.summary,
                    district=place.district,
                    upazila=place.upazila,
                    village=place.village,
                    latitude=place.latitude,
                    longitude=place.longitude,
                    best_season=place.best_season,
                    suggested_duration=place.suggested_duration,
                    budget_min_bdt=float(place.budget_min_bdt) if place.budget_min_bdt is not None else None,
                    budget_max_bdt=float(place.budget_max_bdt) if place.budget_max_bdt is not None else None,
                    average_rating=round(float(avg_rating), 1),
                    review_count=int(review_count),
                    primary_image_url=primary_image_url,
                    tags=tags,
                )
            )

        return cards

    def get_approved_place_by_slug(self, slug: str) -> Optional[PlaceDetailRead]:
        """Fetch detailed information for an approved place by slug."""
        place = (
            self.db.query(Place)
            .options(
                joinedload(Place.aliases),
                joinedload(Place.tags),
                joinedload(Place.media),
            )
            .filter(Place.slug == slug, Place.status == "approved")
            .first()
        )
        if not place:
            return None

        # Calculate rating aggregates
        stats = (
            self.db.query(
                func.coalesce(func.avg(Review.rating), 0.0).label("avg_rating"),
                func.count(Review.id).label("review_count"),
            )
            .filter(
                Review.place_id == place.id,
                Review.status == "published",
                Review.deleted_at.is_(None),
            )
            .first()
        )
        avg_rating = round(float(stats.avg_rating), 1) if stats else 0.0
        review_count = int(stats.review_count) if stats else 0

        aliases = [a.alias for a in place.aliases]
        tags = [t.tag for t in place.tags]
        media_items = [
            PlaceMediaRead.model_validate(m)
            for m in sorted(place.media, key=lambda x: x.sort_order)
            if m.moderation_status == "approved"
        ]

        return PlaceDetailRead(
            id=place.id,
            slug=place.slug,
            name=place.name,
            category=place.category,
            summary=place.summary,
            description=place.description,
            source_type=place.source_type,
            status=place.status,
            village=place.village,
            upazila=place.upazila,
            district=place.district,
            division=place.division,
            nearest_hub=place.nearest_hub,
            latitude=place.latitude,
            longitude=place.longitude,
            best_season=place.best_season,
            suggested_duration=place.suggested_duration,
            guide_requirement=place.guide_requirement,
            budget_min_bdt=float(place.budget_min_bdt) if place.budget_min_bdt is not None else None,
            budget_max_bdt=float(place.budget_max_bdt) if place.budget_max_bdt is not None else None,
            highlights=place.highlights or [],
            know_before_you_go=place.know_before_you_go or [],
            average_rating=avg_rating,
            review_count=review_count,
            aliases=aliases,
            tags=tags,
            media=media_items,
            created_at=place.created_at,
            updated_at=place.updated_at,
        )

    def get_place_by_id(self, place_id: uuid.UUID) -> Optional[Place]:
        return self.db.query(Place).filter(Place.id == place_id).first()

    def format_place_detail(self, place: Place) -> PlaceDetailRead:
        """Format Place ORM object to PlaceDetailRead schema regardless of status."""
        stats = (
            self.db.query(
                func.coalesce(func.avg(Review.rating), 0.0).label("avg_rating"),
                func.count(Review.id).label("review_count"),
            )
            .filter(
                Review.place_id == place.id,
                Review.status == "published",
                Review.deleted_at.is_(None),
            )
            .first()
        )
        avg_rating = round(float(stats.avg_rating), 1) if stats else 0.0
        review_count = int(stats.review_count) if stats else 0

        aliases = [a.alias for a in place.aliases] if place.aliases else []
        tags = [t.tag for t in place.tags] if place.tags else []
        media_items = (
            [PlaceMediaRead.model_validate(m) for m in sorted(place.media, key=lambda x: x.sort_order)]
            if place.media
            else []
        )

        return PlaceDetailRead(
            id=place.id,
            slug=place.slug,
            name=place.name,
            category=place.category,
            summary=place.summary,
            description=place.description,
            source_type=place.source_type,
            status=place.status,
            village=place.village,
            upazila=place.upazila,
            district=place.district,
            division=place.division,
            nearest_hub=place.nearest_hub,
            latitude=place.latitude,
            longitude=place.longitude,
            best_season=place.best_season,
            suggested_duration=place.suggested_duration,
            guide_requirement=place.guide_requirement,
            budget_min_bdt=float(place.budget_min_bdt) if place.budget_min_bdt is not None else None,
            budget_max_bdt=float(place.budget_max_bdt) if place.budget_max_bdt is not None else None,
            highlights=place.highlights or [],
            know_before_you_go=place.know_before_you_go or [],
            average_rating=avg_rating,
            review_count=review_count,
            aliases=aliases,
            tags=tags,
            media=media_items,
            created_at=place.created_at,
            updated_at=place.updated_at,
        )

