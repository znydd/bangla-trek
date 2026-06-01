import uuid
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.group_activity import GroupActivity
from app.models.group_trip import GroupTrip, GroupTripMember
from app.models.poll import Poll, PollOption, Vote
from app.models.user import User
from app.schemas.group_collaboration import PollCreate


class CollaborationService:
    def __init__(self, db: Session):
        self.db = db

    # ── Activity Feed ──

    def log_activity(
        self,
        trip_id: uuid.UUID,
        user_id: uuid.UUID,
        activity_type: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> GroupActivity:
        activity = GroupActivity(
            trip_id=trip_id,
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            metadata_json=metadata,
        )
        self.db.add(activity)
        self.db.flush()
        return activity

    def get_activity_feed(
        self, trip_id: uuid.UUID, limit: int = 50
    ) -> List[dict]:
        query = (
            select(GroupActivity, User)
            .join(User, GroupActivity.user_id == User.id)
            .where(GroupActivity.trip_id == trip_id)
            .order_by(GroupActivity.created_at.desc())
            .limit(limit)
        )
        results = self.db.execute(query).all()
        
        feed = []
        for activity, user in results:
            feed.append({
                "id": activity.id,
                "trip_id": activity.trip_id,
                "user_id": activity.user_id,
                "user_name": user.name,
                "user_picture_url": user.picture_url,
                "activity_type": activity.activity_type,
                "description": activity.description,
                "metadata_json": activity.metadata_json,
                "created_at": activity.created_at,
            })
        return feed

    # ── Polling ──

    def create_poll(
        self, trip_id: uuid.UUID, user_id: uuid.UUID, payload: PollCreate
    ) -> Poll:
        poll = Poll(
            trip_id=trip_id,
            creator_id=user_id,
            title=payload.title,
            description=payload.description,
        )
        self.db.add(poll)
        self.db.flush()

        for opt in payload.options:
            option = PollOption(
                poll_id=poll.id,
                text=opt.text,
                image_url=opt.image_url,
                itinerary_activity_id=opt.itinerary_activity_id,
            )
            self.db.add(option)
        
        self.log_activity(
            trip_id,
            user_id,
            "poll_created",
            f"started a new poll: {poll.title}",
            {"poll_id": str(poll.id)}
        )
        
        # Notify via Messaging API
        try:
            from app.services.messaging_service import MessagingService
            messaging = MessagingService(self.db)
            creator = self.db.query(User).filter(User.id == user_id).first()
            messaging.notify_poll_result(
                trip_id=trip_id,
                title=poll.title,
                creator_name=creator.name if creator else "An owner"
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to send poll notification: {e}")

        self.db.commit()
        self.db.refresh(poll)
        return poll

    def get_polls(self, trip_id: uuid.UUID, current_user_id: uuid.UUID) -> List[dict]:
        query = (
            select(Poll)
            .where(Poll.trip_id == trip_id)
            .order_by(Poll.created_at.desc())
            .options(selectinload(Poll.options).selectinload(PollOption.votes))
        )
        polls = self.db.execute(query).scalars().all()
        
        results = []
        for poll in polls:
            creator = self.db.get(User, poll.creator_id)
            options_data = []
            total_votes = 0
            my_vote_option_id = None
            
            for opt in poll.options:
                vote_count = len(opt.votes)
                total_votes += vote_count
                is_voted_by_me = any(v.user_id == current_user_id for v in opt.votes)
                if is_voted_by_me:
                    my_vote_option_id = opt.id
                
                options_data.append({
                    "id": opt.id,
                    "poll_id": opt.poll_id,
                    "text": opt.text,
                    "image_url": opt.image_url,
                    "itinerary_activity_id": opt.itinerary_activity_id,
                    "vote_count": vote_count,
                    "is_voted_by_me": is_voted_by_me
                })
            
            results.append({
                "id": poll.id,
                "trip_id": poll.trip_id,
                "creator_id": poll.creator_id,
                "creator_name": creator.name if creator else "Unknown",
                "title": poll.title,
                "description": poll.description,
                "is_active": poll.is_active,
                "created_at": poll.created_at,
                "options": options_data,
                "total_votes": total_votes,
                "my_vote_option_id": my_vote_option_id
            })
            
        return results

    def vote(
        self, poll_id: uuid.UUID, user_id: uuid.UUID, option_id: uuid.UUID
    ) -> Vote:
        # Check if option belongs to poll
        option = (
            self.db.execute(
                select(PollOption).where(
                    and_(PollOption.id == option_id, PollOption.poll_id == poll_id)
                )
            )
            .scalar_one_or_none()
        )
        if not option:
            raise ValueError("Option not found in this poll")

        # Check for existing vote in this poll
        existing = (
            self.db.execute(
                select(Vote).where(and_(Vote.poll_id == poll_id, Vote.user_id == user_id))
            )
            .scalar_one_or_none()
        )
        
        if existing:
            if existing.poll_option_id == option_id:
                return existing # Already voted for this
            # Change vote
            existing.poll_option_id = option_id
            vote = existing
        else:
            vote = Vote(
                poll_id=poll_id,
                poll_option_id=option_id,
                user_id=user_id,
            )
            self.db.add(vote)

        poll = self.db.get(Poll, poll_id)
        self.log_activity(
            poll.trip_id,
            user_id,
            "voted",
            f"voted for '{option.text}' in poll: {poll.title}",
            {"poll_id": str(poll_id), "option_id": str(option_id)}
        )
        
        self.db.commit()
        self.db.refresh(vote)
        return vote

    # ── Itinerary Linking ──

    def link_itinerary(
        self, trip_id: uuid.UUID, user_id: uuid.UUID, itinerary_id: uuid.UUID
    ) -> GroupTrip:
        trip = self.db.get(GroupTrip, trip_id)
        if not trip:
            raise ValueError("Trip not found")
        
        # Check permission (only owner/creator for now)
        if trip.creator_id != user_id:
            raise PermissionError("Only the trip creator can link an itinerary")

        trip.itinerary_id = itinerary_id
        
        self.log_activity(
            trip_id,
            user_id,
            "itinerary_linked",
            "linked a shared itinerary to the trip",
            {"itinerary_id": str(itinerary_id)}
        )
        
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
