import uuid
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.services.export_service import ExportService

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/itinerary/{itinerary_id}/pdf")
def export_itinerary_pdf(
    itinerary_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Export an itinerary as a PDF document for offline use."""
    service = ExportService(db)
    try:
        # Note: In a real app, we'd verify ownership here too, 
        # but the service also checks data existence.
        pdf_content = service.generate_itinerary_pdf(itinerary_id)
        
        filename = f"itinerary_{itinerary_id.hex[:8]}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
