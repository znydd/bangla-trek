import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.community import (
    CommunityEntryCreate,
    CommunityEntryList,
    CommunityMapPoint,
    CommunityEntryRead,
    CommunityEntryUpdate,
)
from app.services.community_service import CommunityService
from app.services.cloudinary_service import CloudinaryService

router = APIRouter(prefix="/community-entries", tags=["community"])


@router.get("/", response_model=CommunityEntryList)
def list_entries(
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=100),
    category: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "newest",
    db: Session = Depends(get_db),
):
    service = CommunityService(db)
    items, total = service.list_entries(
        page=page,
        per_page=per_page,
        category=category,
        tag=tag,
        search=search,
        sort_by=sort_by,
    )
    
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


@router.get("/map", response_model=List[CommunityMapPoint])
def list_map_points(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(1000, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    service = CommunityService(db)
    return service.list_map_points(
        category=category,
        tag=tag,
        search=search,
        limit=limit,
    )


@router.get("/{entry_id}", response_model=CommunityEntryRead)
def get_entry(entry_id: uuid.UUID, db: Session = Depends(get_db)):
    service = CommunityService(db)
    try:
        return service.get_entry(entry_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=CommunityEntryRead)
def create_entry(
    payload: CommunityEntryCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = CommunityService(db)
    return service.create_entry(uuid.UUID(user_id), payload)


@router.put("/{entry_id}", response_model=CommunityEntryRead)
def update_entry(
    entry_id: uuid.UUID,
    payload: CommunityEntryUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = CommunityService(db)
    try:
        return service.update_entry(entry_id, uuid.UUID(user_id), payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{entry_id}")
def delete_entry(
    entry_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = CommunityService(db)
    try:
        service.delete_entry(entry_id, uuid.UUID(user_id))
        return {"detail": "Entry deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{entry_id}/photos", response_model=CommunityEntryRead)
async def upload_photos(
    entry_id: uuid.UUID,
    files: List[UploadFile] = File(...),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = CommunityService(db)
    uid = uuid.UUID(user_id)
    
    try:
        # Check ownership first
        service.get_entry(entry_id) # ensures exists
        
        for file in files:
            upload_result = CloudinaryService.upload_image(file)
            service.add_photo(
                entry_id, 
                uid, 
                upload_result["url"], 
                upload_result["public_id"]
            )
            
        return service.get_entry(entry_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{entry_id}/photos/{photo_id}", response_model=CommunityEntryRead)
def delete_photo(
    entry_id: uuid.UUID,
    photo_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = CommunityService(db)
    try:
        service.delete_photo(entry_id, photo_id, uuid.UUID(user_id))
        return service.get_entry(entry_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
