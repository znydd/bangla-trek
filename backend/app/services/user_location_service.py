import math
import uuid
from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_location import UserLocation
from app.schemas.user_location import UserLocationPoint, UserLocationRead, UserLocationUpsert


class UserLocationService:
    def __init__(self, db: Session):
        self.db = db

    def get_me(self, user_id: uuid.UUID) -> Optional[UserLocationRead]:
        loc = (
            self.db.execute(select(UserLocation).where(UserLocation.user_id == user_id))
            .scalar_one_or_none()
        )
        return UserLocationRead.model_validate(loc) if loc else None

    def upsert_me(self, user_id: uuid.UUID, payload: UserLocationUpsert) -> UserLocationRead:
        existing = (
            self.db.execute(select(UserLocation).where(UserLocation.user_id == user_id))
            .scalar_one_or_none()
        )

        if existing:
            existing.latitude = payload.latitude
            existing.longitude = payload.longitude
            existing.status = payload.status
            existing.message = payload.message
            # updated_at is set via onupdate=func.now()
            self.db.add(existing)
            self.db.commit()
            self.db.refresh(existing)
            return UserLocationRead.model_validate(existing)

        loc = UserLocation(
            user_id=user_id,
            latitude=payload.latitude,
            longitude=payload.longitude,
            status=payload.status,
            message=payload.message,
        )
        self.db.add(loc)
        self.db.commit()
        self.db.refresh(loc)
        return UserLocationRead.model_validate(loc)

    def delete_me(self, user_id: uuid.UUID) -> bool:
        loc = (
            self.db.execute(select(UserLocation).where(UserLocation.user_id == user_id))
            .scalar_one_or_none()
        )
        if not loc:
            return False
        self.db.delete(loc)
        self.db.commit()
        return True

    def list_nearby(
        self,
        *,
        lat: float,
        lng: float,
        radius_km: float = 25,
        status: str | None = None,
        exclude_user_id: uuid.UUID | None = None,
        limit: int = 200,
    ) -> list[UserLocationPoint]:
        """
        Returns nearby user locations within a simple bounding box.
        This avoids PostGIS and is good enough for map discovery UX.
        """
        radius_km = max(0.1, min(radius_km, 500.0))

        lat_delta = radius_km / 111.0
        lng_delta = radius_km / (111.0 * max(0.1, math.cos(math.radians(lat))))

        stmt = (
            select(UserLocation, User.name, User.picture_url)
            .join(User, User.id == UserLocation.user_id)
            .where(UserLocation.latitude.between(lat - lat_delta, lat + lat_delta))
            .where(UserLocation.longitude.between(lng - lng_delta, lng + lng_delta))
            .limit(limit)
        )

        if status:
            stmt = stmt.where(UserLocation.status == status)
        if exclude_user_id:
            stmt = stmt.where(UserLocation.user_id != exclude_user_id)

        rows: Iterable[tuple[UserLocation, str, str | None]] = self.db.execute(stmt).all()
        points: list[UserLocationPoint] = []
        for loc, name, picture_url in rows:
            base = UserLocationPoint.model_validate(loc)
            base.user_name = name
            base.user_picture_url = picture_url
            points.append(base)
        return points

