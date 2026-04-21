import uuid
from typing import List, Tuple

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.group_trip import GroupTrip, GroupTripMember
from app.models.user import User
from app.schemas.group_trip import GroupTripCreate, GroupTripUpdate


class GroupTripService:
    def __init__(self, db: Session):
        self.db = db

    def create_trip(self, user_id: uuid.UUID, payload: GroupTripCreate) -> GroupTrip:
        trip = GroupTrip(
            creator_id=user_id,
            title=payload.title,
            destination=payload.destination,
            description=payload.description,
            start_date=payload.start_date,
            end_date=payload.end_date,
            visibility=payload.visibility,
        )
        self.db.add(trip)
        self.db.flush()

        # Add creator as owner member
        member = GroupTripMember(
            trip_id=trip.id,
            user_id=user_id,
            role="owner",
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(trip)
        return trip

    def get_trip(self, trip_id: uuid.UUID) -> GroupTrip:
        trip = (
            self.db.execute(
                select(GroupTrip)
                .where(GroupTrip.id == trip_id)
                .options(selectinload(GroupTrip.members))
            )
            .scalar_one_or_none()
        )
        if not trip:
            raise ValueError("Trip not found")
        return trip

    def get_trip_by_invite_code(self, invite_code: str) -> GroupTrip:
        trip = (
            self.db.execute(
                select(GroupTrip).where(GroupTrip.invite_code == invite_code)
            )
            .scalar_one_or_none()
        )
        if not trip:
            raise ValueError("Invalid invite code")
        return trip

    def list_public_trips(
        self,
        page: int = 1,
        per_page: int = 12,
    ) -> Tuple[List[dict], int]:
        """List all public trips."""
        base = select(GroupTrip).where(GroupTrip.visibility == "public")

        # Count
        count_q = select(func.count()).select_from(base.subquery())
        total = self.db.execute(count_q).scalar() or 0

        # Paginated results
        trips = (
            self.db.execute(
                base.order_by(GroupTrip.created_at.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
            .scalars()
            .all()
        )

        return self._enrich_trip_list(trips), total

    def list_my_trips(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        per_page: int = 12,
    ) -> Tuple[List[dict], int]:
        """List trips the user has created or joined."""
        my_trip_ids = (
            select(GroupTripMember.trip_id)
            .where(GroupTripMember.user_id == user_id)
            .scalar_subquery()
        )

        base = select(GroupTrip).where(GroupTrip.id.in_(my_trip_ids))

        # Count
        count_q = select(func.count()).select_from(base.subquery())
        total = self.db.execute(count_q).scalar() or 0

        # Paginated results
        trips = (
            self.db.execute(
                base.order_by(GroupTrip.created_at.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
            .scalars()
            .all()
        )

        return self._enrich_trip_list(trips), total

    def _enrich_trip_list(self, trips) -> List[dict]:
        """Add member_count and creator info to a list of trip rows."""
        results = []
        for trip in trips:
            member_count = (
                self.db.execute(
                    select(func.count())
                    .where(GroupTripMember.trip_id == trip.id)
                )
                .scalar() or 0
            )
            creator = self.db.execute(
                select(User).where(User.id == trip.creator_id)
            ).scalar_one()

            results.append({
                "id": trip.id,
                "creator_id": trip.creator_id,
                "title": trip.title,
                "destination": trip.destination,
                "description": trip.description,
                "start_date": trip.start_date,
                "end_date": trip.end_date,
                "visibility": trip.visibility,
                "invite_code": trip.invite_code,
                "member_count": member_count,
                "created_at": trip.created_at,
                "creator_name": creator.name,
                "creator_picture_url": creator.picture_url,
            })

        return results

    def join_trip(self, invite_code: str, user_id: uuid.UUID) -> GroupTrip:
        trip = self.get_trip_by_invite_code(invite_code)

        # Check if already a member
        existing = self.db.execute(
            select(GroupTripMember).where(
                and_(
                    GroupTripMember.trip_id == trip.id,
                    GroupTripMember.user_id == user_id,
                )
            )
        ).scalar_one_or_none()

        if existing:
            raise ValueError("Already a member of this trip")

        member = GroupTripMember(
            trip_id=trip.id,
            user_id=user_id,
            role="member",
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(trip)

        # Notify owner via Messaging API
        try:
            from app.services.messaging_service import MessagingService
            messaging = MessagingService(self.db)
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                messaging.notify_group_join(
                    target_user_id=trip.creator_id,
                    trip_id=trip.id,
                    trip_title=trip.title,
                    joiner_name=user.name
                )
            
            # Also check for travel overlaps for the joiner
            from app.services.buddy_matching_service import BuddyMatchingService
            buddy_service = BuddyMatchingService(self.db)
            buddy_service.notify_overlaps_for_user(user_id)
            
        except Exception as e:
            # Don't fail the join if notification fails
            import logging
            logging.getLogger(__name__).error(f"Failed to send join notification: {e}")

        return trip

    def leave_trip(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> None:
        member = self.db.execute(
            select(GroupTripMember).where(
                and_(
                    GroupTripMember.trip_id == trip_id,
                    GroupTripMember.user_id == user_id,
                )
            )
        ).scalar_one_or_none()

        if not member:
            raise ValueError("Not a member of this trip")
        if member.role == "owner":
            raise PermissionError("Owner cannot leave the trip. Delete it instead.")

        self.db.delete(member)
        self.db.commit()

    def delete_trip(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> None:
        trip = self.get_trip(trip_id)
        if trip.creator_id != user_id:
            raise PermissionError("Only the creator can delete this trip")

        self.db.delete(trip)
        self.db.commit()

    def update_trip(
        self, trip_id: uuid.UUID, user_id: uuid.UUID, payload: GroupTripUpdate
    ) -> GroupTrip:
        trip = self.get_trip(trip_id)
        if trip.creator_id != user_id:
            raise PermissionError("Only the creator can update this trip")

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(trip, field, value)

        self.db.commit()
        self.db.refresh(trip)
        return trip

    def is_member(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        return (
            self.db.execute(
                select(GroupTripMember).where(
                    and_(
                        GroupTripMember.trip_id == trip_id,
                        GroupTripMember.user_id == user_id,
                    )
                )
            ).scalar_one_or_none()
            is not None
        )

    def get_invite_preview(self, invite_code: str) -> dict:
        """Return basic trip info for someone deciding whether to join."""
        trip = self.get_trip_by_invite_code(invite_code)
        creator = self.db.execute(
            select(User).where(User.id == trip.creator_id)
        ).scalar_one()
        member_count = (
            self.db.execute(
                select(func.count()).where(GroupTripMember.trip_id == trip.id)
            ).scalar()
            or 0
        )
        return {
            "id": trip.id,
            "title": trip.title,
            "destination": trip.destination,
            "description": trip.description,
            "start_date": trip.start_date,
            "end_date": trip.end_date,
            "visibility": trip.visibility,
            "member_count": member_count,
            "creator_name": creator.name,
            "creator_picture_url": creator.picture_url,
        }

    def get_trip_detail(self, trip_id: uuid.UUID) -> dict:
        trip = self.get_trip(trip_id)
        creator = self.db.execute(
            select(User).where(User.id == trip.creator_id)
        ).scalar_one()

        members = []
        for m in trip.members:
            user = self.db.execute(
                select(User).where(User.id == m.user_id)
            ).scalar_one()
            members.append({
                "user_id": m.user_id,
                "name": user.name,
                "picture_url": user.picture_url,
                "role": m.role,
                "joined_at": m.joined_at,
            })

        return {
            "id": trip.id,
            "creator_id": trip.creator_id,
            "title": trip.title,
            "destination": trip.destination,
            "description": trip.description,
            "start_date": trip.start_date,
            "end_date": trip.end_date,
            "visibility": trip.visibility,
            "invite_code": trip.invite_code,
            "member_count": len(members),
            "created_at": trip.created_at,
            "creator_name": creator.name,
            "creator_picture_url": creator.picture_url,
            "members": members,
        }

    def discover_overlapping(
        self, user_id: uuid.UUID, destination: str, start_date, end_date
    ) -> List[dict]:
        """Find public trips at the same destination with overlapping dates."""
        # Exclude trips the user is already a member of
        my_trip_ids = (
            select(GroupTripMember.trip_id)
            .where(GroupTripMember.user_id == user_id)
            .scalar_subquery()
        )

        trips = (
            self.db.execute(
                select(GroupTrip).where(
                    and_(
                        GroupTrip.destination == destination,
                        GroupTrip.start_date <= end_date,
                        GroupTrip.end_date >= start_date,
                        GroupTrip.visibility == "public",
                        ~GroupTrip.id.in_(my_trip_ids),
                    )
                )
                .order_by(GroupTrip.start_date)
            )
            .scalars()
            .all()
        )

        results = []
        for trip in trips:
            member_count = (
                self.db.execute(
                    select(func.count()).where(GroupTripMember.trip_id == trip.id)
                ).scalar()
                or 0
            )
            creator = self.db.execute(
                select(User).where(User.id == trip.creator_id)
            ).scalar_one()
            results.append({
                "id": trip.id,
                "title": trip.title,
                "destination": trip.destination,
                "description": trip.description,
                "start_date": trip.start_date,
                "end_date": trip.end_date,
                "visibility": trip.visibility,
                "member_count": member_count,
                "creator_name": creator.name,
                "creator_picture_url": creator.picture_url,
            })

        return results
