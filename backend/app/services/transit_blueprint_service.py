import json
import logging
import uuid
from typing import List, Optional, Tuple

from google import genai
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.models.transit_blueprint import TransitBlueprint, TransitBlueprintStep
from app.models.user import User
from app.schemas.transit_blueprint import TransitBlueprintCreate, ParsePreviewRequest

logger = logging.getLogger(__name__)

# ── Gemini client ──

client = genai.Client(api_key=settings.GEMINI_API_KEY)
MODEL = "gemini-3.1-flash-lite-preview"


def _build_parse_prompt(
    raw_description: str,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
) -> str:
    """Build the LLM prompt to parse a natural-language transit description into structured steps."""

    context = ""
    if origin or destination:
        context = f"\nRoute context: from '{origin or 'unknown'}' to '{destination or 'unknown'}'.\n"

    return f"""You are a transportation expert for Bangladesh. Parse the following natural-language transit description into structured step-by-step directions.
{context}
## Transit Description
{raw_description}

## Instructions
1. Break the description into individual sequential transit steps.
2. For each step, identify the transport mode and provide a clear instruction.
3. Available transport modes: bus, cng, walking, rickshaw, train, launch, boat, ferry, auto, bike, car, mixed, other
4. Estimate duration in minutes and cost in BDT for each step if possible based on the description or your knowledge of Bangladesh transport.
5. If the description mentions costs or durations, use those values. Otherwise estimate reasonable values.

## Output Format
Respond ONLY with a valid JSON object. No markdown, no explanation, just the JSON.
The JSON must have these keys:
- "steps" (array of step objects, each with):
  - "step_number" (integer, starting from 1)
  - "instruction" (string, clear actionable instruction)
  - "mode" (string, one of: bus, cng, walking, rickshaw, train, launch, boat, ferry, auto, bike, car, mixed, other)
  - "estimated_duration_mins" (integer or null)
  - "estimated_cost_bdt" (number or null)
- "total_estimated_duration_mins" (integer or null, sum of all step durations)
- "total_estimated_cost_bdt" (number or null, sum of all step costs)

Example:
{{
  "steps": [
    {{
      "step_number": 1,
      "instruction": "Take a Shyamoli Paribahan bus from Dhaka Sayedabad terminal to Srimangal town. Buses depart every hour.",
      "mode": "bus",
      "estimated_duration_mins": 240,
      "estimated_cost_bdt": 450
    }},
    {{
      "step_number": 2,
      "instruction": "Hire a local CNG auto-rickshaw from Srimangal bus stand to Lawachara National Park entry gate.",
      "mode": "cng",
      "estimated_duration_mins": 20,
      "estimated_cost_bdt": 80
    }},
    {{
      "step_number": 3,
      "instruction": "Walk along the main trail from the entry gate to the observation tower.",
      "mode": "walking",
      "estimated_duration_mins": 25,
      "estimated_cost_bdt": 0
    }}
  ],
  "total_estimated_duration_mins": 285,
  "total_estimated_cost_bdt": 530
}}"""


class TransitBlueprintService:
    def __init__(self, db: Session):
        self.db = db

    def create_blueprint(
        self, user_id: uuid.UUID, request: TransitBlueprintCreate
    ) -> TransitBlueprint:
        """
        Create a new transit blueprint. Calls Gemini to parse the raw description
        into structured steps, then saves both the raw text and the parsed steps.
        """
        # 1. Parse the raw description with Gemini
        parsed = self._call_gemini_parse(
            request.raw_description, request.origin, request.destination
        )

        # 2. Calculate totals from parsed data
        total_duration = parsed.get("total_estimated_duration_mins")
        total_cost = parsed.get("total_estimated_cost_bdt")

        # User-provided values override AI estimates
        if request.estimated_duration_mins is not None:
            total_duration = request.estimated_duration_mins
        if request.estimated_cost_bdt is not None:
            total_cost = request.estimated_cost_bdt

        # 3. Create the blueprint
        blueprint = TransitBlueprint(
            user_id=user_id,
            origin=request.origin,
            destination=request.destination,
            raw_description=request.raw_description,
            estimated_duration_mins=total_duration,
            estimated_cost_bdt=total_cost,
            notes=request.notes,
        )

        # 4. Add parsed steps
        for step_data in parsed.get("steps", []):
            step = TransitBlueprintStep(
                step_number=int(step_data["step_number"]),
                instruction=str(step_data["instruction"]),
                mode=str(step_data.get("mode", "other"))[:30],
                estimated_duration_mins=step_data.get("estimated_duration_mins"),
                estimated_cost_bdt=step_data.get("estimated_cost_bdt"),
            )
            blueprint.steps.append(step)

        self.db.add(blueprint)
        self.db.commit()
        self.db.refresh(blueprint)

        return self.get_blueprint(blueprint.id)

    def parse_preview(self, request: ParsePreviewRequest) -> dict:
        """
        Parse raw text with Gemini and return structured steps WITHOUT saving.
        Used for the frontend preview feature.
        """
        return self._call_gemini_parse(
            request.raw_description, request.origin, request.destination
        )

    def list_blueprints(
        self,
        page: int = 1,
        per_page: int = 12,
        search: Optional[str] = None,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
    ) -> Tuple[List[TransitBlueprint], int]:
        """List transit blueprints with optional filters and pagination."""
        query = (
            select(TransitBlueprint)
            .join(User, TransitBlueprint.user_id == User.id)
            .options(selectinload(TransitBlueprint.steps))
        )

        # Text search across origin, destination, and raw_description
        if search:
            search_filter = or_(
                TransitBlueprint.origin.ilike(f"%{search}%"),
                TransitBlueprint.destination.ilike(f"%{search}%"),
                TransitBlueprint.raw_description.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        if origin:
            query = query.filter(TransitBlueprint.origin.ilike(f"%{origin}%"))

        if destination:
            query = query.filter(TransitBlueprint.destination.ilike(f"%{destination}%"))

        # Count total
        total_stmt = select(func.count()).select_from(query.subquery())
        total = self.db.execute(total_stmt).scalar() or 0

        # Order and paginate
        query = query.order_by(desc(TransitBlueprint.created_at))
        query = query.offset((page - 1) * per_page).limit(per_page)

        items = list(self.db.execute(query).scalars().all())

        # Attach author info and step count
        for item in items:
            item.author_name = item.user.name
            item.author_picture_url = item.user.picture_url
            item.step_count = len(item.steps)

        return items, total

    def get_blueprint(self, blueprint_id: uuid.UUID) -> TransitBlueprint:
        """Get a single transit blueprint with all steps."""
        query = (
            select(TransitBlueprint)
            .where(TransitBlueprint.id == blueprint_id)
            .options(selectinload(TransitBlueprint.steps))
        )
        blueprint = self.db.execute(query).scalar_one_or_none()

        if not blueprint:
            raise ValueError("Transit blueprint not found")

        blueprint.author_name = blueprint.user.name
        blueprint.author_picture_url = blueprint.user.picture_url
        return blueprint

    def get_blueprints_for_route(
        self, origin: str, destination: str
    ) -> List[TransitBlueprint]:
        """
        Find blueprints matching an origin → destination pair.
        Used by route optimization (Member-3) as a fallback for standard API paths.
        """
        query = (
            select(TransitBlueprint)
            .where(
                TransitBlueprint.origin.ilike(f"%{origin}%"),
                TransitBlueprint.destination.ilike(f"%{destination}%"),
            )
            .options(selectinload(TransitBlueprint.steps))
            .order_by(desc(TransitBlueprint.created_at))
            .limit(10)
        )
        items = list(self.db.execute(query).scalars().all())

        for item in items:
            item.author_name = item.user.name
            item.author_picture_url = item.user.picture_url
            item.step_count = len(item.steps)

        return items

    def delete_blueprint(
        self, blueprint_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        """Delete a transit blueprint (owner only)."""
        blueprint = self.get_blueprint(blueprint_id)

        if blueprint.user_id != user_id:
            raise PermissionError("Not authorized to delete this blueprint")

        self.db.delete(blueprint)
        self.db.commit()

    def _call_gemini_parse(
        self,
        raw_description: str,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
    ) -> dict:
        """Call Gemini API to parse transit description into structured steps."""
        prompt = _build_parse_prompt(raw_description, origin, destination)

        try:
            logger.info("Calling Gemini API for transit blueprint parsing")
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
                "Failed to parse transit directions from AI response. Please try again."
            )

        if not isinstance(result, dict) or "steps" not in result:
            raise ValueError("AI response was not a valid transit blueprint.")

        return result
