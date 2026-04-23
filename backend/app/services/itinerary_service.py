import json
import logging
import uuid
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

from google import genai
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.models.community_entry import CommunityEntry
from app.models.itinerary import Itinerary, ItineraryActivity
from app.schemas.itinerary import ItineraryGenerateRequest
from app.services.route_optimizer import RouteOptimizerService


# ── LLM clients ──

gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
GEMINI_MODEL = "gemini-2.0-flash-lite"

try:
    import groq
    groq_client = groq.Groq(api_key=settings.GROQ_API_KEY) if getattr(settings, "GROQ_API_KEY", None) else None
except ImportError:
    groq_client = None

GROQ_MODEL = "llama-3.3-70b-versatile"


def _build_prompt(
    request: ItineraryGenerateRequest,
    community_data: List[CommunityEntry],
) -> str:
    """Build the LLM prompt with user preferences and community data context."""

    # Format community entries as context
    community_context = ""
    if community_data:
        entries_text = []
        for entry in community_data:
            tags_str = ", ".join(entry.tags) if entry.tags else "none"
            amenities_str = ", ".join(entry.amenities) if entry.amenities else "none"
            entries_text.append(
                f"- **{entry.name}** ({entry.category})\n"
                f"  Location: {entry.location}\n"
                f"  Price range: {entry.price_range}\n"
                f"  Tags: {tags_str}\n"
                f"  Amenities: {amenities_str}\n"
                f"  Tips: {entry.travel_tips or 'N/A'}\n"
                f"  Entry ID: {entry.id}"
            )
        community_context = (
            "\n\n## Community-Contributed Data for this Destination\n"
            "Use these real places contributed by travelers when possible. "
            "Reference their Entry ID in the community_entry_id field.\n\n"
            + "\n\n".join(entries_text)
        )

    return f"""You are a travel planning expert for Bangladesh. Generate a detailed hour-by-hour travel itinerary.

## Traveler Preferences
- **Destination**: {request.destination}
- **Duration**: {request.duration_days} day(s)
- **Budget**: {request.budget} BDT
- **Travel Style**: {request.travel_style}
- **Interests**: {', '.join(request.interests) if request.interests else 'general'}
- **Group Type**: {request.group_type}
{community_context}

## Instructions
1. Create a day-by-day, hour-by-hour itinerary.
2. Each activity should have a realistic time slot, description with local cultural insights, and estimated cost in BDT.
3. Categories for activities: food, sightseeing, transport, rest, activity, shopping, culture
4. Prioritize underrated and hidden gem locations.
5. Keep the total estimated costs within the budget of {request.budget} BDT.
6. If a community entry matches an activity, include its Entry ID as community_entry_id (as a string UUID). Otherwise set community_entry_id to null.
7. Include practical travel tips in descriptions (e.g., local transport options, best times to visit).

## Output Format
Respond ONLY with a valid JSON array of activity objects. No markdown, no explanation, just the JSON array.
Each object must have these exact keys:
- "day_number" (integer, starting from 1)
- "start_time" (string, "HH:MM" 24-hour format)
- "end_time" (string, "HH:MM" 24-hour format)
- "title" (string, activity name)
- "description" (string, detailed description with cultural insights and tips)
- "estimated_cost" (number, cost in BDT)
- "location" (string, specific location name)
- "category" (string, one of: food, sightseeing, transport, rest, activity, shopping, culture)
- "community_entry_id" (string UUID or null)

Example:
[
  {{
    "day_number": 1,
    "start_time": "08:00",
    "end_time": "09:00",
    "title": "Breakfast at local restaurant",
    "description": "Start your day with traditional Bengali breakfast...",
    "estimated_cost": 150,
    "location": "Hotel area, Sylhet",
    "category": "food",
    "community_entry_id": null
  }}
]"""


class ItineraryService:
    def __init__(self, db: Session):
        self.db = db

    async def generate_itinerary(
        self, user_id: uuid.UUID, request: ItineraryGenerateRequest
    ) -> Itinerary:
        """
        Generate an AI-powered itinerary using Gemini and community data.
        """
        # 1. Fetch community entries for the destination
        community_data = self._get_community_data(request.destination)

        # 2. Build prompt and call LLM
        prompt = _build_prompt(request, community_data)
        
        try:
            activities_json = self._call_groq(prompt)
        except Exception as e:
            logger.warning("Groq failed, falling back to Gemini: %s", str(e))
            activities_json = self._call_gemini(prompt)

        # 3. Save itinerary to DB
        itinerary = Itinerary(
            user_id=user_id,
            destination=request.destination,
            duration_days=request.duration_days,
            budget=request.budget,
            travel_style=request.travel_style,
            interests=request.interests,
            group_type=request.group_type,
        )

        for activity_data in activities_json:
            community_entry_id = activity_data.get("community_entry_id")
            # Validate the community_entry_id exists if provided
            if community_entry_id:
                try:
                    community_entry_id = uuid.UUID(community_entry_id)
                    # Ensure it actually exists in the DB to prevent ForeignKeyViolation
                    exists = self.db.query(CommunityEntry.id).filter(CommunityEntry.id == community_entry_id).first()
                    if not exists:
                        community_entry_id = None
                except (ValueError, AttributeError):
                    community_entry_id = None

            activity = ItineraryActivity(
                day_number=activity_data["day_number"],
                start_time=str(activity_data["start_time"])[:5],
                end_time=str(activity_data["end_time"])[:5],
                title=str(activity_data["title"])[:255],
                description=str(activity_data["description"]),
                estimated_cost=float(activity_data["estimated_cost"]),
                location=str(activity_data["location"])[:500],
                category=str(activity_data["category"])[:30],
                community_entry_id=community_entry_id,
            )
            itinerary.activities.append(activity)

        self.db.add(itinerary)
        self.db.commit()
        self.db.refresh(itinerary)
        
        # 4. Post-process: Optimize routes for each day
        try:
            await self._optimize_itinerary_routes(itinerary)
        except Exception as e:
            logger.error("Failed to optimize itinerary routes: %s", str(e))

        try:
            from app.services.chat_service import ChatService
            from app.services.messaging_service import MessagingService
            
            chat_service = ChatService(self.db)
            messaging = MessagingService(self.db)
            
            # Get seasonal intel for the destination
            intel = chat_service.get_seasonal_intel(itinerary.destination)
            if intel.get("warnings"):
                # Notify the user about the most severe warning or just the first one
                top_warning = intel["warnings"][0]
                messaging.notify_seasonal_warning(
                    user_id=user_id,
                    destination=itinerary.destination,
                    warning_title=top_warning["title"],
                    warning_content=top_warning["description"]
                )
        except Exception as e:
            logger.error(f"Failed to send seasonal warning: {e}")

        return self.get_itinerary(itinerary.id)

      
    async def _optimize_itinerary_routes(self, itinerary: Itinerary):
        """
        Geographic clustering and path optimization post-processing.
        """
        optimizer = RouteOptimizerService()
        
        # Group activities by day
        days_map = {}
        for act in itinerary.activities:
            if act.day_number not in days_map:
                days_map[act.day_number] = []
            days_map[act.day_number].append(act)
            
        for day_num, day_activities in days_map.items():
            # Only optimize if we have coordinates for most items
            coords_list = []
            for act in day_activities:
                if act.community_entry_id:
                    entry = self.db.query(CommunityEntry).filter(CommunityEntry.id == act.community_entry_id).first()
                    if entry and entry.latitude and entry.longitude:
                        coords_list.append({
                            "id": act.id,
                            "lat": entry.latitude,
                            "lng": entry.longitude,
                            "activity": act
                        })
            
            if len(coords_list) >= 2:
                # Optimize the order of activities with coordinates
                optimized_coords = await optimizer.optimize_route_greedy(coords_list)
                
                # Update times to reflect the new order (simplified: keep original time slots but swap content)
                # Or just update the DB objects in the new order if we have a sort_order field (we don't)
                # Since ItineraryActivity.order_by is day_number, start_time, we swap the start/end times
                original_times = [(act.start_time, act.end_time) for act in day_activities]
                original_times.sort() # Ensure we have them in chronological order
                
                # Note: This is a complex swap, for now we just log it and maybe swap a few properties
                logger.info(f"Optimized Day {day_num} for Itinerary {itinerary.id}")
                
                # To truly minimize backtracking, we'd need to reassign the activities to the sorted time slots
                # For this implementation, we'll just reorder the unvisited list and update times
                # This is a placeholder for a more robust time-shuffling algorithm
                

    def list_user_itineraries(self, user_id: uuid.UUID) -> List[Itinerary]:
        """List all itineraries for a user, newest first."""
        query = (
            select(Itinerary)
            .where(Itinerary.user_id == user_id)
            .options(selectinload(Itinerary.activities))
            .order_by(desc(Itinerary.created_at))
        )
        items = self.db.execute(query).scalars().all()

        # Attach activity_count for list view
        for item in items:
            item.activity_count = len(item.activities)

        return list(items)

    def get_itinerary(self, itinerary_id: uuid.UUID) -> Itinerary:
        """Get a single itinerary with all activities."""
        query = (
            select(Itinerary)
            .where(Itinerary.id == itinerary_id)
            .options(selectinload(Itinerary.activities))
        )
        itinerary = self.db.execute(query).scalar_one_or_none()

        if not itinerary:
            raise ValueError("Itinerary not found")

        return itinerary

    def delete_itinerary(self, itinerary_id: uuid.UUID, user_id: uuid.UUID):
        """Delete an itinerary (owner only)."""
        itinerary = self.get_itinerary(itinerary_id)

        if itinerary.user_id != user_id:
            raise PermissionError("Not authorized to delete this itinerary")

        self.db.delete(itinerary)
        self.db.commit()

    def _get_community_data(self, destination: str) -> List[CommunityEntry]:
        """Fetch community entries matching the destination."""
        query = (
            select(CommunityEntry)
            .where(
                CommunityEntry.location.ilike(f"%{destination}%")
            )
            .limit(20)
        )
        return list(self.db.execute(query).scalars().all())

    def _call_gemini(self, prompt: str) -> list:
        """Call Gemini API and parse the JSON response."""
        try:
            logger.info("Calling Gemini API with model: %s", GEMINI_MODEL)
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )
            logger.info("Gemini API responded successfully")
        except Exception as e:
            logger.error("Gemini API error: %s", str(e))
            raise ValueError(f"AI service error: {str(e)}")

        # Extract text from response
        text = response.text.strip()

        # Clean up markdown code fences if present
        if text.startswith("```"):
            # Remove opening fence (```json or ```)
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3].strip()

        try:
            activities = json.loads(text)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON: %s", text[:500])
            raise ValueError(
                "Failed to parse itinerary from AI response. Please try again."
            )

        if not isinstance(activities, list):
            raise ValueError("AI response was not a list of activities.")

        return activities

    def _call_groq(self, prompt: str) -> list:
        """Call Groq API and parse the JSON response."""
        if not groq_client:
            raise ValueError("Groq client is not initialized (missing API key or package).")
            
        try:
            logger.info("Calling Groq API with model: %s", GROQ_MODEL)
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            logger.info("Groq API responded successfully")
        except Exception as e:
            logger.error("Groq API error: %s", str(e))
            raise ValueError(f"Groq AI service error: {str(e)}")

        text = response.choices[0].message.content.strip()

        # Clean up markdown code fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3].strip()

        try:
            activities = json.loads(text)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON: %s", text[:500])
            raise ValueError(
                "Failed to parse itinerary from AI response. Please try again."
            )

        if not isinstance(activities, list):
            raise ValueError("AI response was not a list of activities.")

        return activities
