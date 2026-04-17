import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.user_location import UserLocationPoint, UserLocationRead, UserLocationUpsert
from app.services.user_location_service import UserLocationService

router = APIRouter(prefix="/user-locations", tags=["user-locations"])


@router.get("/me", response_model=UserLocationRead | None)
def get_my_location(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = UserLocationService(db)
    return service.get_me(uuid.UUID(user_id))


@router.put("/me", response_model=UserLocationRead)
def upsert_my_location(
    payload: UserLocationUpsert,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = UserLocationService(db)
    return service.upsert_me(uuid.UUID(user_id), payload)


@router.delete("/me")
def delete_my_location(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = UserLocationService(db)
    deleted = service.delete_me(uuid.UUID(user_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Location not found")
    return {"message": "Location removed"}


@router.get("/nearby", response_model=list[UserLocationPoint])
def list_nearby_users(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(25, gt=0, le=500),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    service = UserLocationService(db)
    return service.list_nearby(
        lat=lat,
        lng=lng,
        radius_km=radius_km,
        status=status,
        exclude_user_id=uuid.UUID(user_id),
    )

