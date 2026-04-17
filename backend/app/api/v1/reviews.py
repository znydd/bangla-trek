import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.review import (
    EntryReviewCreate,
    EntryReviewList,
    EntryReviewRead,
    EntryReviewUpdate,
)
from app.services.cloudinary_service import CloudinaryService
from app.services.review_service import ReviewService

router = APIRouter(prefix="/community-entries/{entry_id}/reviews", tags=["reviews"])


@router.get("/", response_model=EntryReviewList)
def list_reviews(
    entry_id: uuid.UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(6, ge=1, le=50),
    travel_style: Optional[str] = Query(
        None, pattern="^(budget|luxury|adventure|family)$"
    ),
    sort_by: str = Query("newest", pattern="^(newest|highest_rating|lowest_rating)$"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = ReviewService(db)
    try:
        items, total, summary, my_review_id = service.list_reviews(
            entry_id=entry_id,
            user_id=uuid.UUID(user_id),
            page=page,
            per_page=per_page,
            travel_style=travel_style,
            sort_by=sort_by,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    total_pages = (total + per_page - 1) // per_page
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "summary": summary,
        "my_review_id": my_review_id,
    }


@router.post("/", response_model=EntryReviewRead)
def create_review(
    entry_id: uuid.UUID,
    payload: EntryReviewCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = ReviewService(db)
    try:
        return service.create_review(entry_id, uuid.UUID(user_id), payload)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        if "already reviewed" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{review_id}", response_model=EntryReviewRead)
def update_review(
    entry_id: uuid.UUID,
    review_id: uuid.UUID,
    payload: EntryReviewUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = ReviewService(db)
    try:
        return service.update_review(entry_id, review_id, uuid.UUID(user_id), payload)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{review_id}")
def delete_review(
    entry_id: uuid.UUID,
    review_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = ReviewService(db)
    try:
        service.delete_review(entry_id, review_id, uuid.UUID(user_id))
        return {"detail": "Review deleted"}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{review_id}/photos", response_model=EntryReviewRead)
async def upload_review_photos(
    entry_id: uuid.UUID,
    review_id: uuid.UUID,
    files: List[UploadFile] = File(...),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = ReviewService(db)
    uid = uuid.UUID(user_id)
    try:
        review = service.get_review_for_read(entry_id, review_id)
        if review.user_id != uid:
            raise PermissionError("Not authorized to add photos to this review")

        for file in files:
            upload_result = CloudinaryService.upload_image(
                file, folder="bangla-trek/reviews"
            )
            review = service.add_photo(
                entry_id,
                review_id,
                uid,
                upload_result["url"],
                upload_result["public_id"],
            )
        return review
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{review_id}/photos/{photo_id}", response_model=EntryReviewRead)
def delete_review_photo(
    entry_id: uuid.UUID,
    review_id: uuid.UUID,
    photo_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = ReviewService(db)
    try:
        return service.delete_photo(entry_id, review_id, photo_id, uuid.UUID(user_id))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
