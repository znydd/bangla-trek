import statistics
import uuid
from datetime import UTC, datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy import and_, desc, func, select
from sqlalchemy.orm import Session

from app.models.transit_fare_contribution import TransitFareContribution
from app.schemas.transit_fare import TransitFareContributionCreate

FARE_MODES = ("cng", "bus", "train")


def _normalize_route_text(value: str) -> str:
    return value.strip().lower()


class TransitFareService:
    def __init__(self, db: Session):
        self.db = db

    def _attach_author(self, contribution: TransitFareContribution) -> None:
        contribution.author_name = contribution.user.name
        contribution.author_picture_url = contribution.user.picture_url

    def create_contribution(
        self, user_id: uuid.UUID, payload: TransitFareContributionCreate
    ) -> TransitFareContribution:
        if (
            payload.min_fare_bdt is not None
            and payload.max_fare_bdt is not None
            and payload.min_fare_bdt > payload.max_fare_bdt
        ):
            raise ValueError("Minimum fare cannot be greater than maximum fare")

        contribution = TransitFareContribution(
            user_id=user_id,
            origin=payload.origin.strip(),
            destination=payload.destination.strip(),
            mode=payload.mode,
            fare_bdt=payload.fare_bdt,
            min_fare_bdt=payload.min_fare_bdt,
            max_fare_bdt=payload.max_fare_bdt,
            notes=payload.notes,
            source_type=payload.source_type,
            travel_date=payload.travel_date,
        )
        self.db.add(contribution)
        self.db.commit()
        self.db.refresh(contribution)
        self._attach_author(contribution)
        return contribution

    def list_contributions(
        self,
        page: int = 1,
        per_page: int = 20,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        mode: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Tuple[list[TransitFareContribution], int]:
        query = select(TransitFareContribution)

        if origin:
            query = query.where(TransitFareContribution.origin.ilike(f"%{origin.strip()}%"))
        if destination:
            query = query.where(
                TransitFareContribution.destination.ilike(f"%{destination.strip()}%")
            )
        if mode:
            query = query.where(TransitFareContribution.mode == mode)
        if date_from:
            query = query.where(TransitFareContribution.submitted_at >= date_from)
        if date_to:
            query = query.where(TransitFareContribution.submitted_at <= date_to)

        total_stmt = select(func.count()).select_from(query.subquery())
        total = self.db.execute(total_stmt).scalar() or 0

        query = (
            query.order_by(desc(TransitFareContribution.submitted_at))
            .offset((page - 1) * per_page)
            .limit(per_page)
        )

        items = list(self.db.execute(query).scalars().all())
        for item in items:
            self._attach_author(item)
        return items, total

    def delete_contribution(self, contribution_id: uuid.UUID, user_id: uuid.UUID) -> None:
        contribution = self.db.get(TransitFareContribution, contribution_id)
        if not contribution:
            raise ValueError("Fare contribution not found")
        if contribution.user_id != user_id:
            raise PermissionError("Not authorized to delete this fare contribution")

        self.db.delete(contribution)
        self.db.commit()

    def get_estimates(
        self,
        origin: str,
        destination: str,
        mode: Optional[str] = None,
        recent_days: int = 180,
        min_recent_samples: int = 3,
    ) -> dict:
        normalized_origin = _normalize_route_text(origin)
        normalized_destination = _normalize_route_text(destination)

        modes = (mode,) if mode else FARE_MODES

        estimates = [
            self._compute_mode_estimate(
                normalized_origin=normalized_origin,
                normalized_destination=normalized_destination,
                mode_value=mode_value,
                recent_days=recent_days,
                min_recent_samples=min_recent_samples,
            )
            for mode_value in modes
        ]

        return {
            "origin": origin.strip(),
            "destination": destination.strip(),
            "estimates": estimates,
        }

    def _compute_mode_estimate(
        self,
        normalized_origin: str,
        normalized_destination: str,
        mode_value: str,
        recent_days: int,
        min_recent_samples: int,
    ) -> dict:
        base_filters = and_(
            func.lower(func.trim(TransitFareContribution.origin)) == normalized_origin,
            func.lower(func.trim(TransitFareContribution.destination))
            == normalized_destination,
            TransitFareContribution.mode == mode_value,
        )

        recent_cutoff = datetime.now(UTC) - timedelta(days=recent_days)
        recent_rows = self.db.execute(
            select(
                TransitFareContribution.fare_bdt,
                TransitFareContribution.submitted_at,
            ).where(
                base_filters,
                TransitFareContribution.submitted_at >= recent_cutoff,
            )
        ).all()

        all_rows = recent_rows
        used_all_time_fallback = False
        if len(recent_rows) < min_recent_samples:
            all_rows = self.db.execute(
                select(
                    TransitFareContribution.fare_bdt,
                    TransitFareContribution.submitted_at,
                ).where(base_filters)
            ).all()
            used_all_time_fallback = True

        fares = [float(row.fare_bdt) for row in all_rows]
        median_fare = round(float(statistics.median(fares)), 2) if fares else None
        min_fare = round(min(fares), 2) if fares else None
        max_fare = round(max(fares), 2) if fares else None
        last_updated_at = max((row.submitted_at for row in all_rows), default=None)

        return {
            "mode": mode_value,
            "median_fare_bdt": median_fare,
            "submission_count": len(all_rows),
            "recent_submission_count": len(recent_rows),
            "min_fare_bdt": min_fare,
            "max_fare_bdt": max_fare,
            "last_updated_at": last_updated_at,
            "sample_window_days": None if used_all_time_fallback else recent_days,
            "is_low_data": len(all_rows) < min_recent_samples,
            "used_all_time_fallback": used_all_time_fallback,
        }

    @staticmethod
    def get_booking_links() -> dict:
        return {
            "items": [
                {
                    "id": "shohoz",
                    "label": "Shohoz (Bus/Launch/Train Tickets)",
                    "url": "https://www.shohoz.com/",
                },
                {
                    "id": "railway_eticket",
                    "label": "Bangladesh Railway e-Ticket",
                    "url": "https://eticket.railway.gov.bd/",
                },
            ]
        }
