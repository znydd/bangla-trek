import uuid
from typing import Tuple

from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_unread_notifications(self, user_id: uuid.UUID) -> Tuple[list, int]:
        notifications = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).order_by(Notification.created_at.desc()).all()
        return notifications, len(notifications)

    def mark_as_read(self, user_id: uuid.UUID, notification_id: uuid.UUID):
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        if not notification:
            raise ValueError("Notification not found")
        notification.is_read = True
        self.db.commit()
        
    def mark_all_as_read(self, user_id: uuid.UUID):
        self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        self.db.commit()
