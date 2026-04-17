import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.transit_blueprint import (
    ParsePreviewRequest,
    ParsePreviewResponse,
    TransitBlueprintCreate,
    TransitBlueprintListResponse,
    TransitBlueprintRead,
    TransitBlueprintListItem,
)
from app.services.transit_blueprint_service import TransitBlueprintService

router = APIRouter(prefix="/transit-blueprints", tags=["transit-blueprints"])


@router.post("/", response_model=TransitBlueprintRead)
def create_transit_blueprint(
    payload: TransitBlueprintCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Create a new transit blueprint. The LLM parses the raw description into structured steps."""
    service = TransitBlueprintService(db)
    try:
        return service.create_blueprint(uuid.UUID(user_id), payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/parse-preview", response_model=ParsePreviewResponse)
def parse_preview(
    payload: ParsePreviewRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Parse raw transit description with the LLM and return structured steps without saving."""
    service = TransitBlueprintService(db)
    try:
        return service.parse_preview(payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/", response_model=TransitBlueprintListResponse)
def list_transit_blueprints(
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search origin, destination, or description"),
    origin: Optional[str] = Query(None, description="Filter by origin"),
    destination: Optional[str] = Query(None, description="Filter by destination"),
    db: Session = Depends(get_db),
):
    """List all transit blueprints with optional search/filter and pagination."""
    service = TransitBlueprintService(db)
    items, total = service.list_blueprints(
        page=page,
        per_page=per_page,
        search=search,
        origin=origin,
        destination=destination,
    )

    total_pages = (total + per_page - 1) // per_page

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


@router.get("/route", response_model=List[TransitBlueprintListItem])
def get_route_blueprints(
    origin: str = Query(..., description="Route origin"),
    destination: str = Query(..., description="Route destination"),
    db: Session = Depends(get_db),
):
    """Find transit blueprints for a specific route (used as fallback when mapping APIs fail)."""
    service = TransitBlueprintService(db)
    return service.get_blueprints_for_route(origin, destination)


@router.get("/{blueprint_id}", response_model=TransitBlueprintRead)
def get_transit_blueprint(
    blueprint_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Get a single transit blueprint with all steps."""
    service = TransitBlueprintService(db)
    try:
        return service.get_blueprint(blueprint_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{blueprint_id}")
def delete_transit_blueprint(
    blueprint_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Delete a transit blueprint (owner only)."""
    service = TransitBlueprintService(db)
    try:
        service.delete_blueprint(blueprint_id, uuid.UUID(user_id))
        return {"detail": "Transit blueprint deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
