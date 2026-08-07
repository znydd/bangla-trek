import urllib.parse
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.trip import TravelTrip, TravelTripMember, TravelTripRequirement
from app.models.user import User
from app.schemas.trip import (
    EmailDraftRead,
    TravelTripCreate,
    TravelTripDetailRead,
    TravelTripMemberPublicRead,
    TravelTripParticipantRead,
    TravelTripRead,
    TravelTripRequirementRead,
    TravelTripUpdate,
)


class TripService:
    def __init__(self, db: Session):
        self.db = db

    def list_public_trips(
        self,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[TravelTripRead]:
        """Fetch scheduled and full public trips."""
        query = (
            self.db.query(TravelTrip)
            .options(joinedload(TravelTrip.creator), joinedload(TravelTrip.members))
            .filter(TravelTrip.status.in_(["scheduled", "full"]))
        )

        if origin:
            query = query.filter(func.lower(TravelTrip.origin).contains(origin.strip().lower()))

        if destination:
            query = query.filter(func.lower(TravelTrip.destination).contains(destination.strip().lower()))

        trips = query.order_by(TravelTrip.start_at.asc()).offset(skip).limit(limit).all()

        results = []
        for t in trips:
            joined_count = sum(1 for m in t.members if m.status == "joined")
            results.append(
                TravelTripRead(
                    id=t.id,
                    creator_id=t.creator_id,
                    creator_name=t.creator.name,
                    creator_picture_url=t.creator.picture_url,
                    title=t.title,
                    origin=t.origin,
                    destination=t.destination,
                    start_at=t.start_at,
                    end_at=t.end_at,
                    transport=t.transport,
                    estimated_cost_min_bdt=float(t.estimated_cost_min_bdt) if t.estimated_cost_min_bdt is not None else None,
                    estimated_cost_max_bdt=float(t.estimated_cost_max_bdt) if t.estimated_cost_max_bdt is not None else None,
                    max_members=t.max_members,
                    joined_members_count=joined_count,
                    status=t.status,
                    created_at=t.created_at,
                )
            )
        return results

    def get_trip_detail(self, trip_id: uuid.UUID) -> TravelTripDetailRead:
        """Fetch public trip detail with requirement list and public member cards (NO emails)."""
        trip = (
            self.db.query(TravelTrip)
            .options(
                joinedload(TravelTrip.creator),
                joinedload(TravelTrip.requirements),
                joinedload(TravelTrip.members).joinedload(TravelTripMember.user),
            )
            .filter(TravelTrip.id == trip_id)
            .first()
        )
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")

        public_members = [
            TravelTripMemberPublicRead(
                user_id=m.user_id,
                name=m.user.name,
                picture_url=m.user.picture_url,
                role=m.role,
                status=m.status,
                joined_at=m.joined_at,
            )
            for m in trip.members
            if m.status == "joined" and m.user
        ]

        reqs = [
            TravelTripRequirementRead.model_validate(r)
            for r in sorted(trip.requirements, key=lambda x: x.sort_order)
        ]

        return TravelTripDetailRead(
            id=trip.id,
            creator_id=trip.creator_id,
            creator_name=trip.creator.name,
            creator_picture_url=trip.creator.picture_url,
            title=trip.title,
            origin=trip.origin,
            destination=trip.destination,
            start_at=trip.start_at,
            end_at=trip.end_at,
            meeting_point=trip.meeting_point,
            transport=trip.transport,
            estimated_cost_min_bdt=float(trip.estimated_cost_min_bdt) if trip.estimated_cost_min_bdt is not None else None,
            estimated_cost_max_bdt=float(trip.estimated_cost_max_bdt) if trip.estimated_cost_max_bdt is not None else None,
            description=trip.description,
            itinerary=trip.itinerary,
            max_members=trip.max_members,
            joined_members_count=len(public_members),
            status=trip.status,
            communication_platform=trip.communication_platform,
            communication_note=trip.communication_note,
            requirements=reqs,
            members=public_members,
            created_at=trip.created_at,
            updated_at=trip.updated_at,
        )

    def create_trip(self, creator_id: uuid.UUID, trip_in: TravelTripCreate) -> TravelTripDetailRead:
        """Create a new public trip and insert creator as organizer member."""
        if trip_in.end_at < trip_in.start_at:
            raise HTTPException(status_code=400, detail="End date cannot be earlier than start date.")

        trip = TravelTrip(
            creator_id=creator_id,
            title=trip_in.title,
            origin=trip_in.origin,
            destination=trip_in.destination,
            start_at=trip_in.start_at,
            end_at=trip_in.end_at,
            meeting_point=trip_in.meeting_point,
            transport=trip_in.transport,
            estimated_cost_min_bdt=trip_in.estimated_cost_min_bdt,
            estimated_cost_max_bdt=trip_in.estimated_cost_max_bdt,
            description=trip_in.description,
            itinerary=trip_in.itinerary,
            max_members=trip_in.max_members,
            communication_platform=trip_in.communication_platform,
            communication_note=trip_in.communication_note,
            status="scheduled",
        )
        self.db.add(trip)
        self.db.flush()

        # Add requirements
        if trip_in.requirements:
            for idx, req in enumerate(trip_in.requirements):
                self.db.add(
                    TravelTripRequirement(
                        trip_id=trip.id, requirement=req, sort_order=idx
                    )
                )

        # Add creator as organizer member
        self.db.add(
            TravelTripMember(
                trip_id=trip.id,
                user_id=creator_id,
                role="organizer",
                status="joined",
            )
        )

        self.db.commit()
        return self.get_trip_detail(trip.id)

    def update_trip(
        self, trip_id: uuid.UUID, organizer_id: uuid.UUID, update_in: TravelTripUpdate
    ) -> TravelTripDetailRead:
        """Update trip details (Organizer only)."""
        trip = (
            self.db.query(TravelTrip)
            .filter(TravelTrip.id == trip_id, TravelTrip.creator_id == organizer_id)
            .first()
        )
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found or unauthorized")

        update_data = update_in.model_dump(exclude_unset=True)
        reqs = update_data.pop("requirements", None)

        for field, val in update_data.items():
            setattr(trip, field, val)

        if reqs is not None:
            self.db.query(TravelTripRequirement).filter(
                TravelTripRequirement.trip_id == trip.id
            ).delete()
            for idx, req in enumerate(reqs):
                self.db.add(
                    TravelTripRequirement(
                        trip_id=trip.id, requirement=req, sort_order=idx
                    )
                )

        self.db.commit()
        return self.get_trip_detail(trip.id)

    def join_trip_transactional(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> TravelTripDetailRead:
        """Atomically join a trip with row-level database locking to prevent overbooking."""
        # Row lock using FOR UPDATE
        trip = (
            self.db.query(TravelTrip)
            .filter(TravelTrip.id == trip_id)
            .with_for_update()
            .first()
        )
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")

        if trip.status not in ["scheduled", "full"]:
            raise HTTPException(
                status_code=400, detail=f"Cannot join trip with status '{trip.status}'"
            )

        if trip.creator_id == user_id:
            raise HTTPException(status_code=400, detail="Organizer is already part of the trip")

        # Check existing membership
        existing_member = (
            self.db.query(TravelTripMember)
            .filter(
                TravelTripMember.trip_id == trip_id,
                TravelTripMember.user_id == user_id,
            )
            .first()
        )

        if existing_member and existing_member.status == "joined":
            raise HTTPException(status_code=400, detail="You have already joined this trip.")

        # Check active capacity
        current_joined = (
            self.db.query(func.count(TravelTripMember.id))
            .filter(
                TravelTripMember.trip_id == trip_id,
                TravelTripMember.status == "joined",
            )
            .scalar()
        )

        if current_joined >= trip.max_members:
            raise HTTPException(
                status_code=409, detail="Trip capacity is full. Cannot join."
            )

        if existing_member:
            existing_member.status = "joined"
            existing_member.joined_at = datetime.now(timezone.utc)
            existing_member.left_at = None
        else:
            self.db.add(
                TravelTripMember(
                    trip_id=trip_id,
                    user_id=user_id,
                    role="member",
                    status="joined",
                )
            )

        # Update status to 'full' if capacity reached
        if current_joined + 1 >= trip.max_members:
            trip.status = "full"

        self.db.commit()
        return self.get_trip_detail(trip.id)

    def leave_trip(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        """Leave a joined trip and re-open capacity."""
        member = (
            self.db.query(TravelTripMember)
            .filter(
                TravelTripMember.trip_id == trip_id,
                TravelTripMember.user_id == user_id,
                TravelTripMember.status == "joined",
            )
            .first()
        )
        if not member:
            raise HTTPException(status_code=404, detail="Active membership not found.")

        if member.role == "organizer":
            raise HTTPException(
                status_code=400,
                detail="Organizer cannot leave trip. Cancel the trip instead.",
            )

        member.status = "left"
        member.left_at = datetime.now(timezone.utc)

        # If trip was full, re-open to scheduled
        trip = self.db.query(TravelTrip).filter(TravelTrip.id == trip_id).first()
        if trip and trip.status == "full":
            trip.status = "scheduled"

        self.db.commit()
        return {"message": "Successfully left the trip"}

    def cancel_trip(self, trip_id: uuid.UUID, organizer_id: uuid.UUID) -> dict:
        """Cancel a trip (Organizer only)."""
        trip = (
            self.db.query(TravelTrip)
            .filter(TravelTrip.id == trip_id, TravelTrip.creator_id == organizer_id)
            .first()
        )
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found or unauthorized")

        trip.status = "cancelled"
        self.db.commit()
        return {"message": "Trip cancelled successfully"}

    def delete_trip(self, trip_id: uuid.UUID, organizer_id: uuid.UUID) -> dict:
        """Delete a trip post permanently (Organizer only)."""
        trip = (
            self.db.query(TravelTrip)
            .filter(TravelTrip.id == trip_id, TravelTrip.creator_id == organizer_id)
            .first()
        )
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found or unauthorized")

        self.db.query(TravelTripMember).filter(TravelTripMember.trip_id == trip_id).delete()
        self.db.query(TravelTripRequirement).filter(TravelTripRequirement.trip_id == trip_id).delete()
        self.db.delete(trip)
        self.db.commit()
        return {"message": "Trip deleted successfully"}

    def get_organizer_participants(
        self, trip_id: uuid.UUID, organizer_id: uuid.UUID
    ) -> List[TravelTripParticipantRead]:
        """Fetch participant list with email contacts (ORGANIZER ONLY)."""
        trip = (
            self.db.query(TravelTrip)
            .filter(TravelTrip.id == trip_id, TravelTrip.creator_id == organizer_id)
            .first()
        )
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found or unauthorized")

        members = (
            self.db.query(TravelTripMember)
            .options(joinedload(TravelTripMember.user))
            .filter(
                TravelTripMember.trip_id == trip_id,
                TravelTripMember.status == "joined",
            )
            .all()
        )

        return [
            TravelTripParticipantRead(
                user_id=m.user_id,
                name=m.user.name,
                email=m.user.email,
                picture_url=m.user.picture_url,
                role=m.role,
                status=m.status,
                joined_at=m.joined_at,
            )
            for m in members
            if m.user
        ]

    def get_organizer_email_draft(
        self, trip_id: uuid.UUID, organizer_id: uuid.UUID
    ) -> EmailDraftRead:
        """Generate BCC mailto draft with participant email addresses (ORGANIZER ONLY)."""
        participants = self.get_organizer_participants(trip_id, organizer_id)
        trip = self.db.query(TravelTrip).filter(TravelTrip.id == trip_id).first()

        # Extract emails excluding organizer
        cc_emails = [p.email for p in participants if p.user_id != organizer_id]

        subject = f"Bongo Vromon Trip Update: {trip.title}"
        body = (
            f"Hi Travel Buddies!\n\n"
            f"This is an update regarding our trip '{trip.title}' from {trip.origin} to {trip.destination}.\n"
            f"Departure Date: {trip.start_at.strftime('%Y-%m-%d')}\n"
            f"Meeting Point: {trip.meeting_point or 'TBD'}\n\n"
            f"Looking forward to traveling together!\n"
        )

        cc_str = ",".join(cc_emails)
        gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&cc={urllib.parse.quote(cc_str)}&su={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
        mailto_url = f"mailto:?cc={urllib.parse.quote(cc_str)}&subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"

        return EmailDraftRead(
            trip_id=trip.id,
            trip_title=trip.title,
            bcc_emails=cc_emails,
            subject=subject,
            body=body,
            mailto_url=mailto_url,
            gmail_url=gmail_url,
        )
