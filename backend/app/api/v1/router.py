from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.community import router as community_router
from app.api.v1.itinerary import router as itinerary_router
from app.api.v1.nomad_metrics import router as nomad_metrics_router
from app.api.v1.accommodations import router as accommodations_router
from app.api.v1.group_trips import router as group_trips_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(community_router)
router.include_router(itinerary_router)
router.include_router(nomad_metrics_router)
router.include_router(accommodations_router)
router.include_router(group_trips_router)
