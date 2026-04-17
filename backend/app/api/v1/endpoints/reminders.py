import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.models.itinerary import Itinerary
from app.services.messaging_service import MessagingService

router = APIRouter(prefix="/reminders", tags=["reminders"])

@router.post("/simulate-daily")
def simulate_daily_reminders(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Simultate daily itinerary reminders for the user.
    In a real app, this would be a Cron job/Celery task.
    """
    messaging_service = MessagingService(db)
    
    # Find active itineraries for today
    today = date.today()
    # For simulation, just find ANY itinerary owned by the user
    itineraries = db.query(Itinerary).filter(Itinerary.user_id == uuid.UUID(user_id)).limit(3).all()
    
    count = 0
    for it in itineraries:
        messaging_service.notify_daily_reminder(
            user_id=uuid.UUID(user_id),
            itinerary_title=it.title,
            itinerary_id=it.id
        )
        count += 1
        
    return {"message": f"Successfully simulated {count} daily reminders."}
