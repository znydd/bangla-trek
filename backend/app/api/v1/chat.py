import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.chat import (
    ChatMessageRead,
    ChatResponse,
    ChatSendRequest,
    SeasonalIntelResponse,
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
def send_chat_message(
    payload: ChatSendRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Send a message to refine an itinerary via AI chatbot."""
    service = ChatService(db)
    try:
        result = service.send_message(
            uuid.UUID(user_id), payload.itinerary_id, payload.message
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/{itinerary_id}", response_model=List[ChatMessageRead])
def get_chat_history(
    itinerary_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get chat history for an itinerary."""
    service = ChatService(db)
    try:
        return service.get_history(itinerary_id, uuid.UUID(user_id))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/seasonal-intel/", response_model=SeasonalIntelResponse)
def get_seasonal_intel(
    destination: str = Query(..., min_length=1),
    travel_month: Optional[int] = Query(None, ge=1, le=12),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get seasonal intelligence and monsoon warnings for a destination."""
    service = ChatService(db)
    try:
        return service.get_seasonal_intel(destination, travel_month)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
