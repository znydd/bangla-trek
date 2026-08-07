import re
import uuid
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.place import Place, PlaceAlias, PlaceMedia, PlaceTag
from app.models.review import Review
from app.models.user import User
from app.schemas.contribution import (
    DuplicateCheckMatch,
    DuplicateCheckResponse,
    PlaceDraftCreate,
    PlaceDraftUpdate,
    PlaceSubmissionSubmit,
    UserContributionRead,
)
from app.schemas.place import PlaceMediaRead
from app.schemas.review import ReviewRead, ReviewUserRead
from app.services.review_service import ReviewService


def slugify(text: str) -> str:
    """Generate clean slug from string."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "-", text)


class ContributionService:
    def __init__(self, db: Session):
        self.db = db

    def duplicate_check(
        self,
        name: str,
        district: Optional[str] = None,
        upazila: Optional[str] = None,
    ) -> DuplicateCheckResponse:
        """Search approved and pending places using normalized names, aliases, and locations."""
        clean_name = name.strip().lower()
        norm_name = slugify(name)

        query_builder = self.db.query(Place).filter(
            Place.status.in_(["approved", "pending", "draft"])
        )

        matches = []
        has_exact = False

        # 1. Check exact name match
        exact_places = query_builder.filter(
            or_(
                func.lower(Place.name) == clean_name,
                Place.normalized_name == norm_name,
            )
        ).all()

        for p in exact_places:
            has_exact = True
            matches.append(
                DuplicateCheckMatch(
                    id=p.id,
                    slug=p.slug,
                    name=p.name,
                    category=p.category,
                    district=p.district,
                    upazila=p.upazila,
                    status=p.status,
                    match_reason="Exact name match",
                )
            )

        # 2. Check alias or partial match
        if not has_exact:
            alias_matches = (
                self.db.query(Place)
                .join(PlaceAlias, PlaceAlias.place_id == Place.id)
                .filter(
                    PlaceAlias.normalized_alias.contains(norm_name),
                    Place.status.in_(["approved", "pending"]),
                )
                .all()
            )
            for p in alias_matches:
                if not any(m.id == p.id for m in matches):
                    matches.append(
                        DuplicateCheckMatch(
                            id=p.id,
                            slug=p.slug,
                            name=p.name,
                            category=p.category,
                            district=p.district,
                            upazila=p.upazila,
                            status=p.status,
                            match_reason="Matching alias",
                        )
                    )

        # 3. Check district/upazila partial match
        if not matches and district:
            loc_matches = (
                query_builder.filter(
                    func.lower(Place.district) == district.strip().lower(),
                    func.lower(Place.name).contains(clean_name[:4]) if len(clean_name) >= 4 else True,
                )
                .limit(5)
                .all()
            )
            for p in loc_matches:
                matches.append(
                    DuplicateCheckMatch(
                        id=p.id,
                        slug=p.slug,
                        name=p.name,
                        category=p.category,
                        district=p.district,
                        upazila=p.upazila,
                        status=p.status,
                        match_reason="Nearby location and similar name",
                    )
                )

        return DuplicateCheckResponse(
            query=name,
            has_exact_match=has_exact,
            matches=matches,
        )

    def create_draft_place(self, user_id: uuid.UUID, draft_in: PlaceDraftCreate) -> Place:
        """Create a new place contribution in 'draft' status."""
        base_slug = slugify(draft_in.name)
        slug = base_slug

        # Ensure slug uniqueness
        counter = 1
        while self.db.query(Place).filter(Place.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        place = Place(
            slug=slug,
            name=draft_in.name,
            normalized_name=slugify(draft_in.name),
            category=draft_in.category,
            summary=draft_in.summary,
            description=draft_in.description,
            source_type="community",
            status="draft",
            created_by=user_id,
            village=draft_in.village,
            upazila=draft_in.upazila,
            district=draft_in.district,
            division=draft_in.division,
            nearest_hub=draft_in.nearest_hub,
            latitude=draft_in.latitude,
            longitude=draft_in.longitude,
            best_season=draft_in.best_season,
            suggested_duration=draft_in.suggested_duration,
            guide_requirement=draft_in.guide_requirement,
            budget_min_bdt=draft_in.budget_min_bdt,
            budget_max_bdt=draft_in.budget_max_bdt,
            highlights=draft_in.highlights or [],
            know_before_you_go=draft_in.know_before_you_go or [],
        )
        self.db.add(place)
        self.db.flush()

        # Add aliases
        if draft_in.aliases:
            for alias in set(draft_in.aliases):
                self.db.add(
                    PlaceAlias(
                        place_id=place.id,
                        alias=alias,
                        normalized_alias=slugify(alias),
                    )
                )

        # Add tags
        if draft_in.tags:
            for tag in set(draft_in.tags):
                self.db.add(PlaceTag(place_id=place.id, tag=tag))

        self.db.commit()
        self.db.refresh(place)
        return place

    def update_draft_place(
        self, place_id: uuid.UUID, user_id: uuid.UUID, update_in: PlaceDraftUpdate
    ) -> Place:
        """Update an existing draft or changes_requested place submission."""
        place = (
            self.db.query(Place)
            .filter(
                Place.id == place_id,
                Place.created_by == user_id,
                Place.status.in_(["draft", "changes_requested"]),
            )
            .first()
        )
        if not place:
            raise HTTPException(
                status_code=404,
                detail="Draft place submission not found or edit not allowed.",
            )

        update_data = update_in.model_dump(exclude_unset=True)
        aliases = update_data.pop("aliases", None)
        tags = update_data.pop("tags", None)

        if "name" in update_data and update_data["name"]:
            update_data["normalized_name"] = slugify(update_data["name"])

        for field, val in update_data.items():
            setattr(place, field, val)

        if aliases is not None:
            self.db.query(PlaceAlias).filter(PlaceAlias.place_id == place.id).delete()
            for alias in set(aliases):
                self.db.add(
                    PlaceAlias(
                        place_id=place.id,
                        alias=alias,
                        normalized_alias=slugify(alias),
                    )
                )

        if tags is not None:
            self.db.query(PlaceTag).filter(PlaceTag.place_id == place.id).delete()
            for tag in set(tags):
                self.db.add(PlaceTag(place_id=place.id, tag=tag))

        self.db.commit()
        self.db.refresh(place)
        return place

    def submit_place_contribution(
        self,
        place_id: uuid.UUID,
        user_id: uuid.UUID,
        submit_in: PlaceSubmissionSubmit,
    ) -> Place:
        """Submit a draft place and initial review for admin moderation."""
        place = (
            self.db.query(Place)
            .filter(
                Place.id == place_id,
                Place.created_by == user_id,
                Place.status.in_(["draft", "changes_requested"]),
            )
            .first()
        )
        if not place:
            raise HTTPException(
                status_code=404,
                detail="Draft place submission not found or already submitted.",
            )

        place.status = "pending"

        # Create initial review if supplied
        if submit_in.initial_review:
            review_svc = ReviewService(self.db)
            # Create review with status pending
            review_in = submit_in.initial_review
            review = Review(
                place_id=place.id,
                user_id=user_id,
                status="pending",
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

        self.db.commit()
        self.db.refresh(place)
        return place

    def list_user_contributions(self, user_id: uuid.UUID) -> List[UserContributionRead]:
        """Fetch all place submissions created by the user."""
        places = (
            self.db.query(Place)
            .options(joinedload(Place.media), joinedload(Place.reviews))
            .filter(Place.created_by == user_id)
            .order_by(Place.created_at.desc())
            .all()
        )

        res = []
        for p in places:
            media_items = [PlaceMediaRead.model_validate(m) for m in p.media]
            initial_review_read = None
            if p.reviews:
                r = p.reviews[0]
                user_read = ReviewUserRead(
                    id=r.user.id, name=r.user.name, picture_url=r.user.picture_url
                )
                initial_review_read = ReviewRead(
                    id=r.id,
                    place_id=r.place_id,
                    user_id=r.user_id,
                    user=user_read,
                    status=r.status,
                    rating=r.rating,
                    visited_on=r.visited_on,
                    travel_style=r.travel_style,
                    group_type=r.group_type,
                    group_size=r.group_size,
                    starting_location=r.starting_location,
                    actual_cost_bdt=float(r.actual_cost_bdt) if r.actual_cost_bdt else None,
                    title=r.title,
                    travel_guide=r.travel_guide,
                    created_at=r.created_at,
                    updated_at=r.updated_at,
                )

            res.append(
                UserContributionRead(
                    id=p.id,
                    slug=p.slug,
                    name=p.name,
                    category=p.category,
                    summary=p.summary,
                    status=p.status,
                    district=p.district,
                    upazila=p.upazila,
                    created_at=p.created_at,
                    updated_at=p.updated_at,
                    initial_review=initial_review_read,
                    media=media_items,
                )
            )
        return res
