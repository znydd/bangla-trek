import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.group_trip import (
    GroupTripCreate,
    GroupTripDetail,
    GroupTripList,
    GroupTripPreview,
    GroupTripRead,
    GroupTripUpdate,
    OverlappingTrip,
)
from app.schemas.trip_budget import (
    BudgetSummary,
    GroupTripBudgetRead,
    GroupTripBudgetUpsert,
    GroupTripExpenseCreate,
    GroupTripExpenseRead,
    GroupTripExpenseUpdate,
)
from app.services.group_trip_service import GroupTripService
from app.services.trip_budget_service import TripBudgetService

router = APIRouter(prefix="/group-trips", tags=["group-trips"])


@router.post("/", response_model=GroupTripRead)
def create_trip(
    payload: GroupTripCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = GroupTripService(db)
    trip = service.create_trip(uuid.UUID(user_id), payload)

    # Return with creator info
    return service.get_trip_detail(trip.id)


@router.get("/", response_model=GroupTripList)
def list_public_trips(
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """List all public trips."""
    service = GroupTripService(db)
    items, total = service.list_public_trips(page=page, per_page=per_page)
    total_pages = (total + per_page - 1) // per_page
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


@router.get("/my", response_model=GroupTripList)
def list_my_trips(
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """List trips the current user has created or joined."""
    service = GroupTripService(db)
    items, total = service.list_my_trips(
        uuid.UUID(user_id), page=page, per_page=per_page
    )
    total_pages = (total + per_page - 1) // per_page
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


@router.get("/discover", response_model=List[OverlappingTrip])
def discover_overlapping(
    destination: str = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = GroupTripService(db)
    return service.discover_overlapping(
        uuid.UUID(user_id), destination, start_date, end_date
    )


@router.get("/invite/{invite_code}/preview", response_model=GroupTripPreview)
def invite_preview(
    invite_code: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Basic trip info for someone deciding whether to join via invite link."""
    service = GroupTripService(db)
    try:
        return service.get_invite_preview(invite_code)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{trip_id}", response_model=GroupTripDetail)
def get_trip(
    trip_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = GroupTripService(db)
    try:
        trip = service.get_trip(trip_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Private trips: members only
    if trip.visibility == "private" and not service.is_member(trip_id, uuid.UUID(user_id)):
        raise HTTPException(status_code=403, detail="You must be a member to view this private trip")

    return service.get_trip_detail(trip_id)


@router.put("/{trip_id}", response_model=GroupTripDetail)
def update_trip(
    trip_id: uuid.UUID,
    payload: GroupTripUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = GroupTripService(db)
    try:
        service.update_trip(trip_id, uuid.UUID(user_id), payload)
        return service.get_trip_detail(trip_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/join/{invite_code}", response_model=GroupTripDetail)
def join_trip(
    invite_code: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = GroupTripService(db)
    try:
        trip = service.join_trip(invite_code, uuid.UUID(user_id))
        return service.get_trip_detail(trip.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{trip_id}/leave")
def leave_trip(
    trip_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = GroupTripService(db)
    try:
        service.leave_trip(trip_id, uuid.UUID(user_id))
        return {"detail": "Left the trip"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{trip_id}")
def delete_trip(
    trip_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = GroupTripService(db)
    try:
        service.delete_trip(trip_id, uuid.UUID(user_id))
        return {"detail": "Trip deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/{trip_id}/budget", response_model=GroupTripBudgetRead | None)
def get_budget(
    trip_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = TripBudgetService(db)
    try:
        return service.get_budget(trip_id, uuid.UUID(user_id))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.put("/{trip_id}/budget", response_model=GroupTripBudgetRead)
def upsert_budget(
    trip_id: uuid.UUID,
    payload: GroupTripBudgetUpsert,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = TripBudgetService(db)
    try:
        return service.upsert_budget(trip_id, uuid.UUID(user_id), payload)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/{trip_id}/budget/summary", response_model=BudgetSummary)
def budget_summary(
    trip_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = TripBudgetService(db)
    try:
        return service.get_summary(trip_id, uuid.UUID(user_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/{trip_id}/expenses", response_model=list[GroupTripExpenseRead])
def list_expenses(
    trip_id: uuid.UUID,
    limit: int = Query(200, ge=1, le=1000),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = TripBudgetService(db)
    try:
        return service.list_expenses(trip_id, uuid.UUID(user_id), limit=limit)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{trip_id}/expenses", response_model=GroupTripExpenseRead)
def create_expense(
    trip_id: uuid.UUID,
    payload: GroupTripExpenseCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = TripBudgetService(db)
    try:
        return service.create_expense(trip_id, uuid.UUID(user_id), payload)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.put("/{trip_id}/expenses/{expense_id}", response_model=GroupTripExpenseRead)
def update_expense(
    trip_id: uuid.UUID,
    expense_id: uuid.UUID,
    payload: GroupTripExpenseUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = TripBudgetService(db)
    try:
        return service.update_expense(trip_id, expense_id, uuid.UUID(user_id), payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{trip_id}/expenses/{expense_id}")
def delete_expense(
    trip_id: uuid.UUID,
    expense_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = TripBudgetService(db)
    try:
        service.delete_expense(trip_id, expense_id, uuid.UUID(user_id))
        return {"detail": "Expense deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
