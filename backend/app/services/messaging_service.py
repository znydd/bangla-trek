import logging
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.user import User

logger = logging.getLogger(__name__)

class MessagingService:
    """Simulation of Messaging API to handle emails and in-app notifications."""

    def __init__(self, db: Session):
        self.db = db

    def _send_email_sim(self, to_email: str, subject: str, content: str):
        """Simulate sending an email by logging to console/logs."""
        logger.info(f"--- EMAIL SIMULATION ---")
        logger.info(f"To: {to_email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Content: {content}")
        logger.info(f"-------------------------")

    def create_notification(
        self, 
        user_id: uuid.UUID, 
        type: str, 
        title: str, 
        content: str, 
        link_url: Optional[str] = None
    ) -> Notification:
        """Create an in-app notification for the user."""
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            content=content,
            link_url=link_url
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def notify_group_join(self, target_user_id: uuid.UUID, trip_id: uuid.UUID, trip_title: str, joiner_name: str):
        """Notify trip owner that someone joined their trip."""
        content = f"{joiner_name} has joined your group trip '{trip_title}'."
        title = "New Trip Member"
        link_url = f"/trips/{trip_id}"
        
        # Create in-app notification
        self.create_notification(target_user_id, "group_join", title, content, link_url)
        
        # Simulate email to owner
        user = self.db.query(User).filter(User.id == target_user_id).first()
        if user and user.email:
            self._send_email_sim(
                user.email,
                f"New traveler joined: {trip_title}",
                f"Hi {user.name},\n\nGreat news! {joiner_name} has joined your group trip '{trip_title}'. Check it out here: {link_url}"
            )

    def notify_travel_overlap(self, user_id: uuid.UUID, friend_name: str, destination: str, trip_id: Optional[uuid.UUID] = None):
        """Notify user that a friend/connection is traveling to the same place."""
        content = f"Your connection {friend_name} is also planning a trip to {destination} during overlapping dates!"
        title = "Travel Overlap Alert"
        link_url = f"/trips/{trip_id}" if trip_id else "/buddy-matching"
        
        self.create_notification(user_id, "travel_overlap", title, content, link_url)
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if user and user.email:
            self._send_email_sim(
                user.email,
                f"Travel Overlap in {destination}!",
                f"Hi {user.name},\n\nWe noticed that {friend_name} is visiting {destination} at the same time as you. Why not coordinate a meetup? {link_url}"
            )

    def notify_daily_reminder(self, user_id: uuid.UUID, itinerary_title: str, itinerary_id: uuid.UUID):
        """Daily reminder for upcoming itinerary."""
        content = f"Today's Itinerary: {itinerary_title}. Don't forget to check your schedule!"
        title = "Trip Reminder"
        link_url = f"/planner/{itinerary_id}"
        
        self.create_notification(user_id, "reminder", title, content, link_url)
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if user and user.email:
            self._send_email_sim(
                user.email,
                f"Daily Reminder: {itinerary_title}",
                f"Hi {user.name},\n\nReady for today's adventure? Here's your itinerary for {itinerary_title}: {link_url}"
            )
