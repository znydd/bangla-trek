import json
import logging
import math
import uuid
from typing import List, Optional, Tuple

from google import genai
from sqlalchemy import desc, func, select, or_, text
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.models.community_entry import CommunityEntry
from app.models.itinerary import Itinerary, ItineraryActivity
from app.models.user import User

logger = logging.getLogger(__name__)

# ── Gemini client ──

client = genai.Client(api_key=settings.GEMINI_API_KEY)
MODEL = "gemini-3.1-flash-lite-preview"

# Accommodation categories we filter on
ACCOMMODATION_CATEGORIES = ("hotel", "guesthouse", "homestay")


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two lat/lng points."""
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class AccommodationService:
    def __init__(self, db: Session):
        self.db = db

    def search_accommodations(
        self,
        page: int = 1,
        per_page: int = 12,
        accommodation_type: Optional[str] = None,
        price_range: Optional[str] = None,
        amenities: Optional[List[str]] = None,
        search: Optional[str] = None,
        sort_by: str = "newest",
        ref_lat: Optional[float] = None,
        ref_lng: Optional[float] = None,
    ) -> Tuple[List[CommunityEntry], int]:
        """
        Search accommodation entries (hotel/guesthouse/homestay) with filters.
        Returns entries with optional computed distance from a reference point.
        """
        # Base query — only accommodation categories
        query = (
            select(CommunityEntry)
            .join(User, CommunityEntry.user_id == User.id)
            .options(
                selectinload(CommunityEntry.photos),
            )
        )

        # Filter to accommodation categories only
        if accommodation_type and accommodation_type in ACCOMMODATION_CATEGORIES:
            query = query.filter(CommunityEntry.category == accommodation_type)
        else:
            query = query.filter(
                CommunityEntry.category.in_(ACCOMMODATION_CATEGORIES)
            )

        # Price range filter
        if price_range:
            query = query.filter(CommunityEntry.price_range == price_range)

        # Amenities filter — entries that have ALL requested amenities
        if amenities:
            for amenity in amenities:
                query = query.filter(CommunityEntry.amenities.any(amenity))

        # Text search
        if search:
            search_filter = or_(
                CommunityEntry.name.ilike(f"%{search}%"),
                CommunityEntry.location.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        # Sorting
        if sort_by == "name":
            query = query.order_by(CommunityEntry.name)
        elif sort_by == "price_asc":
            # Sort by price_range field (budget < mid_range < premium < luxury)
            price_order = func.array_position(
                text("ARRAY['budget', 'mid_range', 'premium', 'luxury']"),
                CommunityEntry.price_range,
            )
            query = query.order_by(price_order)
        elif sort_by == "price_desc":
            price_order = func.array_position(
                text("ARRAY['budget', 'mid_range', 'premium', 'luxury']"),
                CommunityEntry.price_range,
            )
            query = query.order_by(desc(price_order))
        else:  # default: newest
            query = query.order_by(desc(CommunityEntry.created_at))

        # Count total
        total_stmt = select(func.count()).select_from(query.subquery())
        total = self.db.execute(total_stmt).scalar() or 0

        # Pagination
        query = query.offset((page - 1) * per_page).limit(per_page)
        items = list(self.db.execute(query).scalars().all())

        # Attach author info and compute distance
        for item in items:
            item.author_name = item.user.name
            item.author_picture_url = item.user.picture_url
            if (
                ref_lat is not None
                and ref_lng is not None
                and item.latitude is not None
                and item.longitude is not None
            ):
                item.distance_km = round(
                    _haversine_km(ref_lat, ref_lng, item.latitude, item.longitude), 1
                )
            else:
                item.distance_km = None

        # If sorting by distance and we have a reference point, sort in Python
        if sort_by == "distance" and ref_lat is not None and ref_lng is not None:
            items.sort(
                key=lambda x: x.distance_km if x.distance_km is not None else float("inf")
            )

        return items, total

    def get_accommodation(self, entry_id: uuid.UUID) -> CommunityEntry:
        """Get a single accommodation entry by ID."""
        query = (
            select(CommunityEntry)
            .where(
                CommunityEntry.id == entry_id,
                CommunityEntry.category.in_(ACCOMMODATION_CATEGORIES),
            )
            .options(
                selectinload(CommunityEntry.photos),
                selectinload(CommunityEntry.video_embeds),
            )
        )
        entry = self.db.execute(query).scalar_one_or_none()

        if not entry:
            raise ValueError("Accommodation not found")

        entry.author_name = entry.user.name
        entry.author_picture_url = entry.user.picture_url
        entry.distance_km = None
        return entry

    def get_ai_recommendations(self, itinerary_id: uuid.UUID) -> dict:
        """
        Generate AI-powered accommodation recommendations for an itinerary.
        Uses Gemini to analyze itinerary activities and suggest strategically
        positioned accommodations with cost-benefit reasoning.
        """
        # 1. Fetch the itinerary with activities
        itin_query = (
            select(Itinerary)
            .where(Itinerary.id == itinerary_id)
            .options(selectinload(Itinerary.activities))
        )
        itinerary = self.db.execute(itin_query).scalar_one_or_none()
        if not itinerary:
            raise ValueError("Itinerary not found")

        # 2. Fetch all accommodations near the destination
        accom_query = (
            select(CommunityEntry)
            .where(
                CommunityEntry.category.in_(ACCOMMODATION_CATEGORIES),
                CommunityEntry.location.ilike(f"%{itinerary.destination}%"),
            )
            .options(selectinload(CommunityEntry.photos))
            .limit(30)
        )
        accommodations = list(self.db.execute(accom_query).scalars().all())

        # 3. Build prompt
        prompt = self._build_recommendation_prompt(itinerary, accommodations)

        # 4. Call Gemini
        result = self._call_gemini(prompt)

        return {
            "recommendations": result.get("recommendations", []),
            "summary": result.get("summary", "No recommendations available."),
            "itinerary_id": itinerary_id,
        }

    def _build_recommendation_prompt(
        self,
        itinerary: Itinerary,
        accommodations: List[CommunityEntry],
    ) -> str:
        """Build the LLM prompt for accommodation recommendations."""

        # Format itinerary activities
        activities_text = []
        for act in itinerary.activities:
            activities_text.append(
                f"  - Day {act.day_number} | {act.start_time}-{act.end_time} | "
                f"{act.title} @ {act.location} (category: {act.category})"
            )
        activities_str = "\n".join(activities_text) if activities_text else "No activities planned yet."

        # Format available accommodations
        accom_text = []
        if accommodations:
            for acc in accommodations:
                amenities_str = ", ".join(acc.amenities) if acc.amenities else "none listed"
                lat_lng = ""
                if acc.latitude and acc.longitude:
                    lat_lng = f"  GPS: {acc.latitude}, {acc.longitude}"
                accom_text.append(
                    f"  - ID: {acc.id}\n"
                    f"    Name: {acc.name}\n"
                    f"    Type: {acc.category}\n"
                    f"    Location: {acc.location}\n"
                    f"    Price Range: {acc.price_range}\n"
                    f"    Amenities: {amenities_str}\n"
                    f"    Tips: {acc.travel_tips or 'N/A'}\n"
                    f"{lat_lng}"
                )
        accom_str = "\n\n".join(accom_text) if accom_text else "No accommodations in database for this area."

        return f"""You are a travel accommodation expert for Bangladesh. Analyze the traveler's itinerary and recommend the best accommodations from the available options.

## Traveler's Trip
- **Destination**: {itinerary.destination}
- **Duration**: {itinerary.duration_days} day(s)
- **Budget**: {itinerary.budget} BDT total trip budget
- **Travel Style**: {itinerary.travel_style}
- **Group Type**: {itinerary.group_type}

## Planned Activities
{activities_str}

## Available Accommodations
{accom_str}

## Instructions
1. Recommend up to 3 accommodations that are strategically positioned to minimize daily travel distances to the planned attractions.
2. For each recommendation, provide a cost-benefit analysis comparing price vs. convenience.
3. Consider the traveler's budget and travel style when making recommendations.
4. Rate each accommodation's travel convenience on a scale of 1-10.
5. If no accommodations are available in the database, suggest what type of accommodation would be ideal and provide general guidance.

## Output Format
Respond ONLY with a valid JSON object (no markdown, no explanation). The JSON must have these keys:
- "summary" (string): A 2-3 sentence overview of your accommodation strategy for this trip.
- "recommendations" (array): Up to 3 recommendation objects, each with:
  - "accommodation_id" (string): The ID from the available accommodations list, or "suggested" if not in database
  - "name" (string): Accommodation name
  - "category" (string): hotel, guesthouse, or homestay
  - "price_range" (string): budget, mid_range, premium, or luxury
  - "location" (string): Location description
  - "reasoning" (string): 2-3 sentences explaining why this is a good choice, focusing on proximity to attractions and travel efficiency
  - "estimated_cost_per_night" (number): Estimated cost per night in BDT
  - "travel_convenience_score" (integer 1-10): How convenient this location is for the planned activities
  - "cost_benefit_summary" (string): One sentence comparing cost vs. benefits

Example:
{{
  "summary": "For your budget trip to Sylhet...",
  "recommendations": [
    {{
      "accommodation_id": "uuid-here-or-suggested",
      "name": "Hilltop Guesthouse",
      "category": "guesthouse",
      "price_range": "budget",
      "location": "Near Jaflong, Sylhet",
      "reasoning": "This guesthouse is centrally located...",
      "estimated_cost_per_night": 1500,
      "travel_convenience_score": 8,
      "cost_benefit_summary": "Excellent value at 1500 BDT/night with walking distance to 3 attractions."
    }}
  ]
}}"""

    def _call_gemini(self, prompt: str) -> dict:
        """Call Gemini API and parse the JSON response."""
        try:
            logger.info("Calling Gemini API for accommodation recommendations")
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
            )
            logger.info("Gemini API responded successfully")
        except Exception as e:
            logger.error("Gemini API error: %s", str(e))
            raise ValueError(f"AI service error: {str(e)}")

        text = response.text.strip()

        # Clean up markdown code fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3].strip()

        try:
            result = json.loads(text)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON: %s", text[:500])
            raise ValueError(
                "Failed to parse recommendations from AI response. Please try again."
            )

        if not isinstance(result, dict):
            raise ValueError("AI response was not a valid recommendation object.")

        return result
