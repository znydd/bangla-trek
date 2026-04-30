from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.community import router as community_router
from app.api.v1.itinerary import router as itinerary_router
from app.api.v1.nomad_metrics import router as nomad_metrics_router
from app.api.v1.accommodations import router as accommodations_router
from app.api.v1.group_trips import router as group_trips_router
from app.api.v1.route_optimizer import router as route_optimizer_router
from app.api.v1.emergency import router as emergency_router
from app.api.v1.reviews import router as reviews_router
from app.api.v1.transit_blueprints import router as transit_blueprints_router
from app.api.v1.transit_fares import router as transit_fares_router
from app.api.v1.user_locations import router as user_locations_router
from app.api.v1.buddy_matching import router as buddy_matching_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(community_router)
router.include_router(itinerary_router)
router.include_router(nomad_metrics_router)
router.include_router(accommodations_router)
router.include_router(group_trips_router)
router.include_router(route_optimizer_router)
router.include_router(emergency_router)
router.include_router(reviews_router)

router.include_router(transit_blueprints_router)
router.include_router(transit_fares_router)

router.include_router(user_locations_router)
router.include_router(buddy_matching_router)
