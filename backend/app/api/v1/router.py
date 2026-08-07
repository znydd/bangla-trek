from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.ai import router as ai_router
from app.api.v1.auth import router as auth_router
from app.api.v1.contributions import router as contributions_router
from app.api.v1.places import router as places_router
from app.api.v1.trips import router as trips_router

router = APIRouter(prefix="/api/v1")

# Shared Infrastructure
router.include_router(auth_router)

# Feature Module 2: Contributions (includes /places/duplicate-check before /places/{slug})
router.include_router(contributions_router)

# Feature Module 1: Places & Reviews
router.include_router(places_router)

# Feature Module 3: AI Travel Assistant
router.include_router(ai_router)

# Feature Module 4: Travel Buddy Public Trips
router.include_router(trips_router)

# Admin Moderation
router.include_router(admin_router)






