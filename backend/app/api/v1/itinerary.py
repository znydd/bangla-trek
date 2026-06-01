import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.itinerary import (
    ItineraryGenerateRequest,
    ItineraryListItem,
    ItineraryRead,
)
from app.services.itinerary_service import ItineraryService

router = APIRouter(prefix="/itineraries", tags=["itineraries"])


@router.post("/generate", response_model=ItineraryRead)
async def generate_itinerary(
    payload: ItineraryGenerateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Generate an AI-powered travel itinerary using Gemini and community data."""
    service = ItineraryService(db)
    try:
        return await service.generate_itinerary(uuid.UUID(user_id), payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/", response_model=List[ItineraryListItem])
def list_itineraries(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """List all itineraries for the current user."""
    service = ItineraryService(db)
    return service.list_user_itineraries(uuid.UUID(user_id))


@router.get("/{itinerary_id}", response_model=ItineraryRead)
def get_itinerary(
    itinerary_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get a single itinerary with all activities."""
    service = ItineraryService(db)
    try:
        return service.get_itinerary(itinerary_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{itinerary_id}")
def delete_itinerary(
    itinerary_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Delete an itinerary (owner only)."""
    service = ItineraryService(db)
    try:
        service.delete_itinerary(itinerary_id, uuid.UUID(user_id))
        return {"detail": "Itinerary deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/{itinerary_id}/export")
def export_itinerary(
    itinerary_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Export an itinerary as a PDF document."""
    from fastapi import Response
    from app.services.export_service import ExportService
    
    # We could check permissions here, but for now we allow anyone with the ID
    # (or we could restrict to members of the trip it belongs to)
    try:
        service = ExportService(db)
        pdf_content = service.generate_itinerary_pdf(itinerary_id)
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=itinerary_{itinerary_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
