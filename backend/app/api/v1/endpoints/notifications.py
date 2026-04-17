import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.models.notification import Notification

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=List[dict])
def get_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Retrieve in-app notifications for the current user."""
    query = (
        select(Notification)
        .where(Notification.user_id == uuid.UUID(user_id))
        .order_by(Notification.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    
    notifications = db.execute(query).scalars().all()
    
    return [
        {
            "id": n.id,
            "type": n.type,
            "title": n.title,
            "content": n.content,
            "link_url": n.link_url,
            "is_read": n.is_read,
            "created_at": n.created_at
        }
        for n in notifications
    ]

@router.patch("/{notification_id}/read")
def mark_read(
    notification_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Mark a notification as read."""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == uuid.UUID(user_id)
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    notification.is_read = True
    db.commit()
    return {"status": "success"}

@router.post("/mark-all-read")
def mark_all_read(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for the current user."""
    db.query(Notification).filter(
        Notification.user_id == uuid.UUID(user_id),
        Notification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    return {"status": "success"}
