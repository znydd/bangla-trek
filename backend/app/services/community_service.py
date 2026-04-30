import math
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.community_entry import CommunityEntry
from app.models.entry_photo import EntryPhoto
from app.models.entry_video_embed import EntryVideoEmbed
from app.models.user import User
from app.schemas.community import CommunityEntryCreate, CommunityEntryUpdate
from .cloudinary_service import CloudinaryService


class CommunityService:
    def __init__(self, db: Session):
        self.db = db

    def list_entries(
        self,
        page: int = 1,
        per_page: int = 12,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "newest",
    ) -> Tuple[List[CommunityEntry], int]:
        """
        List community entries with pagination and filters.
        Joins with User to get author information.
        """
        # Base query joining with User and eager loading nested objects
        query = (
            select(CommunityEntry)
            .join(User, CommunityEntry.user_id == User.id)
            .options(
                selectinload(CommunityEntry.photos),
                selectinload(CommunityEntry.video_embeds),
            )
        )

        # Filters
        if category:
            query = query.filter(CommunityEntry.category == category)
        if tag:
            query = query.filter(CommunityEntry.tags.any(tag))
        if search:
            search_filter = or_(
                CommunityEntry.name.ilike(f"%{search}%"),
                CommunityEntry.location.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        # Sorting
        if sort_by == "name":
            query = query.order_by(CommunityEntry.name)
        else:  # default newest
            query = query.order_by(desc(CommunityEntry.created_at))

        # Count total
        total_stmt = select(func.count()).select_from(query.subquery())
        total = self.db.execute(total_stmt).scalar() or 0

        # Pagination
        query = query.offset((page - 1) * per_page).limit(per_page)
        items = self.db.execute(query).scalars().all()

        # Manually attach author info for schema mapping
        for item in items:
            item.author_name = item.user.name
            item.author_picture_url = item.user.picture_url

        return list(items), total

    def get_entry(self, entry_id: uuid.UUID) -> CommunityEntry:
        """
        Get a single community entry by ID.
        """
        query = (
            select(CommunityEntry)
            .where(CommunityEntry.id == entry_id)
            .options(
                selectinload(CommunityEntry.photos),
                selectinload(CommunityEntry.video_embeds),
            )
        )
        entry = self.db.execute(query).scalar_one_or_none()
        
        if not entry:
            raise ValueError("Entry not found")
        
        # Attach author info
        entry.author_name = entry.user.name
        entry.author_picture_url = entry.user.picture_url
        
        return entry

    def list_map_points(
        self,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 1000,
    ) -> List[CommunityEntry]:
        """
        Returns coordinate-bearing entries for map rendering.
        No pagination-by-page to keep social map markers stable.
        """
        query = (
            select(CommunityEntry)
            .join(User, CommunityEntry.user_id == User.id)
            .where(CommunityEntry.latitude.is_not(None))
            .where(CommunityEntry.longitude.is_not(None))
            .order_by(desc(CommunityEntry.created_at))
            .limit(limit)
        )

        if category:
            query = query.filter(CommunityEntry.category == category)
        if tag:
            query = query.filter(CommunityEntry.tags.any(tag))
        if search:
            search_filter = or_(
                CommunityEntry.name.ilike(f"%{search}%"),
                CommunityEntry.location.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        items = self.db.execute(query).scalars().all()
        for item in items:
            item.author_name = item.user.name
            item.author_picture_url = item.user.picture_url
        return list(items)

    def create_entry(self, user_id: uuid.UUID, payload: CommunityEntryCreate) -> CommunityEntry:
        """
        Create a new community entry.
        """
        data = payload.model_dump(exclude={"video_embeds"})
        entry = CommunityEntry(**data, user_id=user_id)
        
        # Add video embeds
        for video_payload in payload.video_embeds:
            video = EntryVideoEmbed(**video_payload.model_dump(), entry=entry)
            entry.video_embeds.append(video)
            
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        
        return self.get_entry(entry.id)

    def update_entry(
        self, entry_id: uuid.UUID, user_id: uuid.UUID, payload: CommunityEntryUpdate
    ) -> CommunityEntry:
        """
        Update an existing community entry.
        """
        entry = self.get_entry(entry_id)
        
        if entry.user_id != user_id:
            raise PermissionError("Not authorized to update this entry")
            
        update_data = payload.model_dump(exclude_unset=True, exclude={"video_embeds"})
        for key, value in update_data.items():
            setattr(entry, key, value)
            
        # Update video embeds if provided
        if payload.video_embeds is not None:
            # Delete old ones
            for old_video in entry.video_embeds:
                self.db.delete(old_video)
            entry.video_embeds = []
            
            # Add new ones
            for video_payload in payload.video_embeds:
                video = EntryVideoEmbed(**video_payload.model_dump(), entry=entry)
                entry.video_embeds.append(video)
                
        self.db.commit()
        self.db.refresh(entry)
        
        return self.get_entry(entry.id)

    def delete_entry(self, entry_id: uuid.UUID, user_id: uuid.UUID):
        """
        Delete a community entry and its associated photos from Cloudinary.
        """
        entry = self.get_entry(entry_id)
        
        if entry.user_id != user_id:
            raise PermissionError("Not authorized to delete this entry")
            
        # Delete photos from Cloudinary first
        for photo in entry.photos:
            CloudinaryService.delete_image(photo.public_id)
            
        self.db.delete(entry)
        self.db.commit()

    def add_photo(self, entry_id: uuid.UUID, user_id: uuid.UUID, url: str, public_id: str):
        """
        Add a photo to an entry.
        """
        entry = self.get_entry(entry_id)
        if entry.user_id != user_id:
            raise PermissionError("Not authorized to add photos to this entry")
            
        photo = EntryPhoto(entry_id=entry_id, url=url, public_id=public_id)
        self.db.add(photo)
        self.db.commit()
        
    def delete_photo(self, entry_id: uuid.UUID, photo_id: uuid.UUID, user_id: uuid.UUID):
        """
        Delete a photo from an entry and Cloudinary.
        """
        entry = self.get_entry(entry_id)
        if entry.user_id != user_id:
            raise PermissionError("Not authorized to delete photos from this entry")
            
        photo_stmt = select(EntryPhoto).where(
            EntryPhoto.id == photo_id, EntryPhoto.entry_id == entry_id
        )
        photo = self.db.execute(photo_stmt).scalar_one_or_none()
        
        if photo:
            CloudinaryService.delete_image(photo.public_id)
            self.db.delete(photo)
            self.db.commit()
        else:
            raise ValueError("Photo not found")
