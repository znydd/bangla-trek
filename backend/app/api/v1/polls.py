import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.poll import PollCreate, PollRead, PollVoteCreate
from app.services.poll_service import PollService

router = APIRouter(prefix="/trips", tags=["polls"])


@router.get("/{trip_id}/polls", response_model=List[PollRead])
def get_polls(
    trip_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = PollService(db)
    try:
        return service.get_trip_polls(trip_id, uuid.UUID(user_id))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{trip_id}/polls", response_model=PollRead)
def create_poll(
    trip_id: uuid.UUID,
    data: PollCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = PollService(db)
    try:
        poll = service.create_poll(trip_id, uuid.UUID(user_id), data)
        # return newly read poll to get options/stats
        return service.get_trip_polls(trip_id, uuid.UUID(user_id))[0]
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{trip_id}/polls/{poll_id}/vote")
def vote_poll(
    trip_id: uuid.UUID,
    poll_id: uuid.UUID,
    data: PollVoteCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = PollService(db)
    try:
        return service.vote_poll(poll_id, data.option_id, uuid.UUID(user_id))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
