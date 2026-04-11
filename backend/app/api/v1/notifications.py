import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.notification import NotificationList
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=NotificationList)
def get_notifications(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    items, total = service.get_unread_notifications(uuid.UUID(user_id))
    return {"items": items, "total_unread": total}


@router.put("/{notification_id}/read")
def mark_read(
    notification_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    try:
        service.mark_as_read(uuid.UUID(user_id), notification_id)
        return {"status": "ok"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/read-all")
def mark_all_read(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    service.mark_all_as_read(uuid.UUID(user_id))
    return {"status": "ok"}
