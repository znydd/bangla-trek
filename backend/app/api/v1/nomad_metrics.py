import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.models.nomad_metrics import NomadMetric
from app.schemas.nomad_metrics import NomadMetricSubmit, NomadMetricSummary, CarrierSignal

router = APIRouter(prefix="/nomad-metrics", tags=["Nomad Metrics"])

SIGNAL_ORDER = {"No Signal": 0, "2G": 1, "3G": 2, "4G": 3, "5G": 4}


@router.post("/")
def submit_metric(
    data: NomadMetricSubmit,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    user_uuid = uuid.UUID(user_id)

    existing = db.execute(
        select(NomadMetric).where(
            NomadMetric.entry_id == data.entry_id,
            NomadMetric.user_id == user_uuid,
        )
    ).scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=409, detail="You have already submitted metrics for this location.")

    metric = NomadMetric(
        entry_id=data.entry_id,
        user_id=user_uuid,
        carrier=data.carrier,
        signal_strength=data.signal_strength,
        safety_rating=data.safety_rating,
        bkash_available=data.bkash_available,
    )
    db.add(metric)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="You have already submitted metrics for this location.")
    return {"message": "Metric submitted successfully"}


@router.get("/{entry_id}", response_model=NomadMetricSummary)
def get_metrics(
    entry_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    user_uuid = uuid.UUID(user_id)

    metrics = db.execute(
        select(NomadMetric).where(NomadMetric.entry_id == entry_id)
    ).scalars().all()

    has_submitted = db.execute(
        select(NomadMetric.id).where(
            NomadMetric.entry_id == entry_id,
            NomadMetric.user_id == user_uuid,
        )
    ).scalar_one_or_none() is not None

    if not metrics:
        return NomadMetricSummary(
            entry_id=entry_id,
            avg_safety_rating=None,
            bkash_available_pct=0,
            signal_by_carrier=[],
            has_submitted=has_submitted,
        )

    avg_safety = sum(m.safety_rating for m in metrics) / len(metrics)
    bkash_pct = int((sum(1 for m in metrics if m.bkash_available) / len(metrics)) * 100)

    carrier_map: dict[tuple, int] = {}
    for m in metrics:
        key = (m.carrier, m.signal_strength)
        carrier_map[key] = carrier_map.get(key, 0) + 1

    signal_by_carrier = [
        CarrierSignal(carrier=carrier, signal=signal, votes=votes)
        for (carrier, signal), votes in sorted(
            carrier_map.items(),
            key=lambda x: (-x[1], -SIGNAL_ORDER.get(x[0][1], 0))
        )
    ]

    return NomadMetricSummary(
        entry_id=entry_id,
        avg_safety_rating=round(avg_safety, 1),
        bkash_available_pct=bkash_pct,
        signal_by_carrier=signal_by_carrier,
        has_submitted=has_submitted,
    )