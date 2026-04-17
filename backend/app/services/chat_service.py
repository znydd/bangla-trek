import json
import logging
import uuid
from typing import List, Optional

from google import genai
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.models.chat_message import ChatMessage
from app.models.community_entry import CommunityEntry
from app.models.itinerary import Itinerary, ItineraryActivity

logger = logging.getLogger(__name__)

# ── Gemini client ──
client = genai.Client(api_key=settings.GEMINI_API_KEY)
MODEL = "gemini-2.0-flash-lite"


class ChatService:
    """Handles AI chatbot interactions for itinerary refinement."""

    def __init__(self, db: Session):
        self.db = db

    # ── Public API ──

    def send_message(
        self, user_id: uuid.UUID, itinerary_id: uuid.UUID, message: str
    ) -> dict:
        """
        Process a user message to refine an itinerary.

        1. Loads itinerary + activities context
        2. Loads recent chat history
        3. Calls Gemini with the refinement prompt
        4. Optionally updates itinerary activities
        5. Saves chat messages (user + assistant)
        6. Returns AI reply + any updated activities
        """
        # Load itinerary
        itinerary = self._get_itinerary(itinerary_id, user_id)

        # Load chat history (last 20 messages for context)
        history = self._get_recent_history(itinerary_id, limit=20)

        # Build prompt
        prompt = self._build_refinement_prompt(itinerary, history, message)

        # Call Gemini
        response_data = self._call_gemini_chat(prompt)

        # Save user message
        user_msg = ChatMessage(
            itinerary_id=itinerary_id,
            user_id=user_id,
            role="user",
            content=message,
        )
        self.db.add(user_msg)

        # Save assistant message
        assistant_msg = ChatMessage(
            itinerary_id=itinerary_id,
            user_id=user_id,
            role="assistant",
            content=response_data["reply"],
        )
        self.db.add(assistant_msg)

        # Apply activity updates if the AI suggested them
        updated_activities = None
        if response_data.get("updated_activities"):
            updated_activities = self._apply_activity_updates(
                itinerary, response_data["updated_activities"]
            )

        self.db.commit()
        self.db.refresh(assistant_msg)

        return {
            "reply": response_data["reply"],
            "updated_activities": updated_activities,
            "message": assistant_msg,
        }

    def get_history(
        self, itinerary_id: uuid.UUID, user_id: uuid.UUID
    ) -> List[ChatMessage]:
        """Get full chat history for an itinerary."""
        # Verify ownership
        self._get_itinerary(itinerary_id, user_id)

        query = (
            select(ChatMessage)
            .where(ChatMessage.itinerary_id == itinerary_id)
            .order_by(ChatMessage.created_at.asc())
        )
        return list(self.db.execute(query).scalars().all())

    def get_seasonal_intel(self, destination: str, travel_month: Optional[int] = None) -> dict:
        """
        Get seasonal intelligence and monsoon warnings for a destination.
        Uses Gemini to generate weather/seasonal recommendations based on
        historical patterns and community feedback.
        """
        # Check for community data about the destination
        community_data = self._get_community_context(destination)

        prompt = self._build_seasonal_prompt(destination, travel_month, community_data)
        return self._call_gemini_seasonal(prompt, destination)

    # ── Private helpers ──

    def _get_itinerary(self, itinerary_id: uuid.UUID, user_id: uuid.UUID) -> Itinerary:
        """Load itinerary with activities, verify ownership."""
        query = (
            select(Itinerary)
            .where(Itinerary.id == itinerary_id)
            .options(selectinload(Itinerary.activities))
        )
        itinerary = self.db.execute(query).scalar_one_or_none()

        if not itinerary:
            raise ValueError("Itinerary not found")
        if itinerary.user_id != user_id:
            raise PermissionError("Not authorized to access this itinerary")

        return itinerary

    def _get_recent_history(self, itinerary_id: uuid.UUID, limit: int = 20) -> List[ChatMessage]:
        """Get the most recent chat messages for context."""
        query = (
            select(ChatMessage)
            .where(ChatMessage.itinerary_id == itinerary_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        messages = list(self.db.execute(query).scalars().all())
        messages.reverse()  # Chronological order
        return messages

    def _get_community_context(self, destination: str) -> List[CommunityEntry]:
        """Fetch community entries matching the destination."""
        query = (
            select(CommunityEntry)
            .where(CommunityEntry.location.ilike(f"%{destination}%"))
            .limit(10)
        )
        return list(self.db.execute(query).scalars().all())

    def _build_refinement_prompt(
        self,
        itinerary: Itinerary,
        history: List[ChatMessage],
        user_message: str,
    ) -> str:
        """Build the Gemini prompt for itinerary refinement."""

        # Format current activities
        activities_text = []
        for a in sorted(itinerary.activities, key=lambda x: (x.day_number, x.start_time)):
            activities_text.append(
                f"  Day {a.day_number} | {a.start_time}-{a.end_time} | "
                f"{a.title} ({a.category}) | {a.location} | ৳{a.estimated_cost}"
            )
        activities_str = "\n".join(activities_text) if activities_text else "  (no activities yet)"

        # Format chat history
        history_text = ""
        if history:
            history_lines = []
            for msg in history[-10:]:  # Last 10 messages
                role_label = "User" if msg.role == "user" else "Assistant"
                history_lines.append(f"  {role_label}: {msg.content[:500]}")
            history_text = "\n".join(history_lines)

        return f"""You are a travel planning assistant for Bangladesh. You are helping refine an existing itinerary through conversation.

## Current Itinerary
- **Destination**: {itinerary.destination}
- **Duration**: {itinerary.duration_days} day(s)
- **Budget**: {itinerary.budget} BDT
- **Travel Style**: {itinerary.travel_style}
- **Interests**: {', '.join(itinerary.interests) if itinerary.interests else 'general'}
- **Group Type**: {itinerary.group_type}

## Current Activities
{activities_str}

## Conversation History
{history_text if history_text else "  (first message)"}

## User's New Message
"{user_message}"

## Instructions
1. Respond naturally and helpfully to the user's request.
2. If the user asks to modify the itinerary (add spots, change budget, rearrange schedule, etc.), include an "updated_activities" array in your response with the COMPLETE updated list of activities.
3. If the user is just asking a question or chatting, respond with just a "reply" text and no updated_activities.
4. Keep suggestions culturally relevant and practical for Bangladesh travel.
5. Respect the budget constraint of {itinerary.budget} BDT unless the user explicitly asks to change it.

## Output Format
Respond ONLY with valid JSON. No markdown, no code fences. The JSON must have:
- "reply" (string): Your conversational response
- "updated_activities" (array or null): If you modified the itinerary, provide the COMPLETE list of all activities. Each activity: {{"day_number": int, "start_time": "HH:MM", "end_time": "HH:MM", "title": str, "description": str, "estimated_cost": number, "location": str, "category": str, "community_entry_id": null}}

Example for a modification:
{{"reply": "I've added more nature spots to your itinerary...", "updated_activities": [...]}}

Example for just a question:
{{"reply": "The best time to visit Sundarbans is..."}}"""

    def _build_seasonal_prompt(
        self,
        destination: str,
        travel_month: Optional[int],
        community_data: List[CommunityEntry],
    ) -> str:
        """Build prompt for seasonal intelligence."""
        month_names = [
            "", "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        month_context = ""
        if travel_month:
            month_context = f"\nThe user is planning to travel in **{month_names[travel_month]}**."

        community_context = ""
        if community_data:
            tips = [
                f"- {entry.name}: {entry.travel_tips}"
                for entry in community_data
                if entry.travel_tips
            ]
            if tips:
                community_context = (
                    "\n\n## Community Tips\n" + "\n".join(tips[:5])
                )

        return f"""You are a Bangladesh travel weather and seasonal expert. Provide seasonal intelligence for the following destination.

## Destination
{destination}{month_context}{community_context}

## Instructions
Provide practical seasonal warnings, monsoon alerts, and travel recommendations for this Bangladesh destination.
Consider:
1. Bangladesh monsoon season (June-October)
2. Cyclone risks for coastal areas
3. Flash flood risks for northeastern areas (Sylhet, Sunamganj)
4. Winter fog affecting transport (December-January)
5. Extreme heat periods (March-May)
6. Festival seasons that may affect availability
7. Best months to visit this specific destination

## Output Format
Respond ONLY with valid JSON:
{{
  "warnings": [
    {{
      "severity": "info|warning|danger",
      "title": "short title",
      "description": "detailed description with practical advice",
      "recommended_months": ["month1", "month2"]
    }}
  ],
  "best_months": ["month1", "month2", "month3"],
  "current_season_summary": "A short paragraph about what to expect right now"
}}"""

    def _call_gemini_chat(self, prompt: str) -> dict:
        """Call Gemini and parse JSON response for chat refinement."""
        try:
            logger.info("Calling Gemini for chat refinement")
            response = client.models.generate_content(
                model=MODEL, contents=prompt
            )
            logger.info("Gemini chat response received")
        except Exception as e:
            logger.error("Gemini chat error: %s", str(e))
            raise ValueError(f"AI service error: {str(e)}")

        text = response.text.strip()

        # Clean markdown fences
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3].strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            logger.error("Failed to parse chat JSON: %s", text[:500])
            # Fallback: treat as plain text reply
            return {"reply": text, "updated_activities": None}

        if not isinstance(data, dict):
            return {"reply": str(data), "updated_activities": None}

        return {
            "reply": data.get("reply", "I couldn't generate a proper response. Please try again."),
            "updated_activities": data.get("updated_activities"),
        }

    def _call_gemini_seasonal(self, prompt: str, destination: str) -> dict:
        """Call Gemini for seasonal intelligence."""
        try:
            logger.info("Calling Gemini for seasonal intel: %s", destination)
            response = client.models.generate_content(
                model=MODEL, contents=prompt
            )
        except Exception as e:
            logger.error("Gemini seasonal error: %s", str(e))
            raise ValueError(f"AI service error: {str(e)}")

        text = response.text.strip()

        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3].strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            logger.error("Failed to parse seasonal JSON: %s", text[:500])
            return {
                "destination": destination,
                "warnings": [],
                "best_months": [],
                "current_season_summary": text[:500],
            }

        return {
            "destination": destination,
            "warnings": data.get("warnings", []),
            "best_months": data.get("best_months", []),
            "current_season_summary": data.get("current_season_summary", ""),
        }

    def _apply_activity_updates(
        self, itinerary: Itinerary, updated_activities: list
    ) -> list:
        """Replace itinerary activities with AI-suggested updates."""
        # Remove old activities
        for activity in itinerary.activities:
            self.db.delete(activity)

        # Add new activities
        new_activities = []
        for act_data in updated_activities:
            community_entry_id = act_data.get("community_entry_id")
            if community_entry_id:
                try:
                    community_entry_id = uuid.UUID(community_entry_id)
                    exists = (
                        self.db.query(CommunityEntry.id)
                        .filter(CommunityEntry.id == community_entry_id)
                        .first()
                    )
                    if not exists:
                        community_entry_id = None
                except (ValueError, AttributeError):
                    community_entry_id = None

            activity = ItineraryActivity(
                itinerary_id=itinerary.id,
                day_number=act_data["day_number"],
                start_time=str(act_data["start_time"])[:5],
                end_time=str(act_data["end_time"])[:5],
                title=str(act_data["title"])[:255],
                description=str(act_data["description"]),
                estimated_cost=float(act_data.get("estimated_cost", 0)),
                location=str(act_data["location"])[:500],
                category=str(act_data.get("category", "activity"))[:30],
                community_entry_id=community_entry_id,
            )
            self.db.add(activity)
            new_activities.append(act_data)

        return new_activities
