import json
import logging
import math
from typing import List, Optional, Tuple

from google import genai
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.config import settings
from app.data.emergency_phrases import EMERGENCY_PHRASES
from app.models.emergency_facility import EmergencyFacility

logger = logging.getLogger(__name__)

# ── Gemini client ──

client = genai.Client(api_key=settings.GEMINI_API_KEY)
MODEL = "gemini-3.1-flash-lite-preview"


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance in km between two points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _build_translate_prompt(text: str, dialect: Optional[str] = None) -> str:
    """Build the LLM prompt to translate an emergency phrase."""
    dialect_instruction = ""
    if dialect and dialect != "standard":
        dialect_instruction = f"""
4. Also translate into the {dialect} dialect of Bengali.
5. Provide the dialect text in both Bengali script and romanized form.
"""

    return f"""You are an expert Bengali language translator specializing in emergency communications for travelers in Bangladesh.

Translate the following English text into Bengali:

"{text}"

Instructions:
1. Provide the translation in standard Bengali script.
2. Provide the romanized (Latin alphabet) version of the Bengali translation.
3. Prioritize clarity and urgency — this is for emergency situations.
{dialect_instruction}

Respond ONLY with a valid JSON object. No markdown, no explanation, just the JSON.
The JSON must have these keys:
- "bengali" (string, Bengali script translation)
- "romanized" (string, romanized Bengali)
- "dialect" (string, the dialect name or "standard")
- "dialect_text" (string or null, dialect version in Bengali script if dialect was requested)
- "dialect_romanized" (string or null, romanized dialect version if dialect was requested)

Example:
{{
  "bengali": "আমার সাহায্য দরকার",
  "romanized": "Amar sahajjo dorkar",
  "dialect": "standard",
  "dialect_text": null,
  "dialect_romanized": null
}}"""


class EmergencyService:
    def __init__(self, db: Session):
        self.db = db

    def list_facilities(
        self,
        facility_type: Optional[str] = None,
        district: Optional[str] = None,
        search: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        limit: int = 50,
    ) -> Tuple[List[EmergencyFacility], int]:
        """List emergency facilities with optional filters. If lat/lng provided, compute distance."""
        query = select(EmergencyFacility)

        if facility_type:
            query = query.where(EmergencyFacility.facility_type == facility_type)

        if district:
            query = query.where(EmergencyFacility.district.ilike(f"%{district}%"))

        if search:
            query = query.where(
                EmergencyFacility.name.ilike(f"%{search}%")
                | EmergencyFacility.address.ilike(f"%{search}%")
                | EmergencyFacility.district.ilike(f"%{search}%")
            )

        # Count total
        total_stmt = select(func.count()).select_from(query.subquery())
        total = self.db.execute(total_stmt).scalar() or 0

        # Fetch all matching
        query = query.limit(limit)
        items = list(self.db.execute(query).scalars().all())

        # Compute distance if lat/lng provided and sort by nearest
        if lat is not None and lng is not None:
            for item in items:
                item.distance_km = round(
                    _haversine(lat, lng, item.latitude, item.longitude), 2
                )
            items.sort(key=lambda x: x.distance_km)

        return items, total

    def get_nearest_facilities(
        self,
        lat: float,
        lng: float,
        facility_type: Optional[str] = None,
        limit: int = 5,
    ) -> List[EmergencyFacility]:
        """Get nearest facilities by GPS coordinates."""
        query = select(EmergencyFacility)

        if facility_type:
            query = query.where(EmergencyFacility.facility_type == facility_type)

        items = list(self.db.execute(query).scalars().all())

        # Compute distance and sort
        for item in items:
            item.distance_km = round(
                _haversine(lat, lng, item.latitude, item.longitude), 2
            )
        items.sort(key=lambda x: x.distance_km)

        return items[:limit]

    def get_emergency_phrases(self) -> list:
        """Return all pre-saved emergency phrases."""
        return EMERGENCY_PHRASES

    def translate_phrase(self, text: str, dialect: Optional[str] = None) -> dict:
        """Call Gemini to translate a custom phrase into Bengali + optional dialect."""
        prompt = _build_translate_prompt(text, dialect)

        try:
            logger.info("Calling Gemini API for emergency translation")
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
            )
            logger.info("Gemini API responded successfully")
        except Exception as e:
            logger.error("Gemini API error: %s", str(e))
            raise ValueError(f"AI translation service error: {str(e)}")

        raw = response.text.strip()

        # Clean up markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3].strip()

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            logger.error("Failed to parse translation JSON: %s", raw[:500])
            raise ValueError(
                "Failed to parse translation from AI. Please try again."
            )

        result["original_text"] = text
        if "dialect" not in result:
            result["dialect"] = dialect or "standard"

        return result
