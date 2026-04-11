import uuid
from typing import List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.poll import Poll, PollOption, PollVote
from app.models.group_trip import GroupTripMember
from app.models.notification import Notification
from app.schemas.poll import PollCreate


class PollService:
    def __init__(self, db: Session):
        self.db = db

    def is_member(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        return self.db.query(GroupTripMember).filter(
            GroupTripMember.trip_id == trip_id,
            GroupTripMember.user_id == user_id
        ).first() is not None

    def create_poll(self, trip_id: uuid.UUID, user_id: uuid.UUID, data: PollCreate) -> Poll:
        if not self.is_member(trip_id, user_id):
            raise PermissionError("Must be a group member to create a poll")

        poll = Poll(
            trip_id=trip_id,
            creator_id=user_id,
            title=data.title,
            category=data.category,
            is_open=True
        )
        self.db.add(poll)
        self.db.flush()

        for opt in data.options:
            option = PollOption(
                poll_id=poll.id,
                title=opt.title,
                description=opt.description
            )
            self.db.add(option)
        
        # Notify other members
        members = self.db.query(GroupTripMember).filter(GroupTripMember.trip_id == trip_id).all()
        for member in members:
            if member.user_id != user_id:
                notif = Notification(
                    user_id=member.user_id,
                    type="poll_created",
                    message=f"A new poll '{poll.title}' was created in your trip.",
                    resource_id=trip_id,
                    resource_type="trip"
                )
                self.db.add(notif)
        
        self.db.commit()
        self.db.refresh(poll)
        return poll

    def get_trip_polls(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> List[dict]:
        if not self.is_member(trip_id, user_id):
            raise PermissionError("Must be a group member to view polls")

        polls = self.db.query(Poll).options(
            joinedload(Poll.creator),
            joinedload(Poll.options).joinedload(PollOption.votes)
        ).filter(Poll.trip_id == trip_id).order_by(Poll.created_at.desc()).all()

        result = []
        for poll in polls:
            options_data = []
            total_votes = 0
            for opt in poll.options:
                opt_votes = len(opt.votes)
                total_votes += opt_votes
                has_voted = any(vote.user_id == user_id for vote in opt.votes)
                options_data.append({
                    "id": opt.id,
                    "poll_id": opt.poll_id,
                    "title": opt.title,
                    "description": opt.description,
                    "vote_count": opt_votes,
                    "has_voted": has_voted
                })
            
            result.append({
                "id": poll.id,
                "trip_id": poll.trip_id,
                "creator_id": poll.creator_id,
                "title": poll.title,
                "category": poll.category,
                "is_open": poll.is_open,
                "created_at": poll.created_at,
                "creator_name": poll.creator.name if poll.creator else "Unknown",
                "options": options_data,
                "total_votes": total_votes
            })
        return result

    def vote_poll(self, poll_id: uuid.UUID, option_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        poll = self.db.query(Poll).filter(Poll.id == poll_id).first()
        if not poll:
            raise ValueError("Poll not found")
        if not poll.is_open:
            raise ValueError("Poll is closed")
        if not self.is_member(poll.trip_id, user_id):
            raise PermissionError("Must be a group member to vote")

        # Remove existing vote if any
        existing_vote = self.db.query(PollVote).filter(
            PollVote.poll_id == poll_id,
            PollVote.user_id == user_id
        ).first()

        if existing_vote:
            if existing_vote.option_id == option_id:
                # Already voted for this, no-op or unvote? Let's just return.
                return {"status": "ok"}
            self.db.delete(existing_vote)

        vote = PollVote(
            poll_id=poll_id,
            option_id=option_id,
            user_id=user_id
        )
        self.db.add(vote)

        # Notify poll creator if it's someone else
        if poll.creator_id != user_id:
            notif = Notification(
                user_id=poll.creator_id,
                type="poll_voted",
                message=f"Someone voted on your poll '{poll.title}'.",
                resource_id=poll.trip_id,
                resource_type="trip"
            )
            self.db.add(notif)
            
        self.db.commit()
        return {"status": "ok"}
