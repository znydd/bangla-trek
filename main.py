import os
import re
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import date, datetime, timezone
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import JSON, Column
from sqlmodel import Field, Session, SQLModel, create_engine, select

load_dotenv()

API_PREFIX = "/api/v1"
DEMO_USER_ID = "demo_user"
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://bongovromon.com")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/bangla_trek",
)

SUPPORTED_TAGS = {"Hidden Gem", "Trending"}
SUPPORTED_VISIBILITY = {"public", "private"}
COMMUNITY_CATEGORIES = {"attraction", "hotel", "guesthouse", "homestay", "restaurant"}
DEFAULT_PRESENCE_COLORS = ["teal", "purple", "amber", "blue", "rose", "emerald"]

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

app = FastAPI(
    title="Bangla Trek API",
    version="0.1.0",
    description="Single-file FastAPI + SQLModel implementation of the BongoVromon API spec.",
)


# =============================================================================
# Core helpers
# =============================================================================


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def isoformat(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:10]}"


def touch(model: Any) -> None:
    if hasattr(model, "updated_at"):
        model.updated_at = utcnow()


def success_response(
    message: str, data: Any = None, meta: dict[str, Any] | None = None
) -> dict[str, Any]:
    payload: dict[str, Any] = {"success": True, "message": message, "data": data}
    if meta is not None:
        payload["meta"] = meta
    return payload


def api_error(
    status_code: int, message: str, errors: dict[str, Any] | None = None
) -> None:
    raise HTTPException(
        status_code=status_code, detail={"message": message, "errors": errors or {}}
    )


def parse_csv_param(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def paginate(
    items: list[Any], page: int, limit: int
) -> tuple[list[Any], dict[str, int]]:
    total = len(items)
    start = (page - 1) * limit
    end = start + limit
    return items[start:end], {"page": page, "limit": limit, "total": total}


def normalize(value: Any) -> str:
    return str(value or "").strip().lower()


def text_match(query: str, *parts: Any) -> bool:
    if not query:
        return True
    combined = " ".join(str(part or "") for part in parts).lower()
    return query.lower() in combined


def build_invite_code(seed: str) -> str:
    prefix = re.sub(r"[^A-Z]", "", seed.upper())[:6] or "TRIP"
    return f"{prefix}{uuid4().hex[:6].upper()}"


def build_invite_link(invite_code: str) -> str:
    return f"{PUBLIC_BASE_URL}/groups/join/{invite_code}"


def ensure_visibility(value: str) -> None:
    if value not in SUPPORTED_VISIBILITY:
        api_error(
            422,
            "Validation failed",
            {
                "visibility": [
                    f"Must be one of: {', '.join(sorted(SUPPORTED_VISIBILITY))}"
                ]
            },
        )


def ensure_tags(tags: list[str]) -> None:
    invalid = [tag for tag in tags if tag not in SUPPORTED_TAGS]
    if invalid:
        api_error(
            422,
            "Validation failed",
            {"tags": [f"Unsupported tag(s): {', '.join(invalid)}"]},
        )


def ensure_price_range(min_value: float | None, max_value: float | None) -> None:
    if min_value is not None and max_value is not None and max_value < min_value:
        api_error(
            422,
            "Validation failed",
            {"price_range_max": ["Must be greater than or equal to price_range_min"]},
        )


def ensure_date_range(start_date: date, end_date: date) -> None:
    if end_date < start_date:
        api_error(
            422,
            "Validation failed",
            {"end_date": ["Must be greater than or equal to start_date"]},
        )


def calculate_itinerary_total(days: list[dict[str, Any]]) -> float:
    total = 0.0
    for day in days:
        for activity in day.get("activities", []):
            total += float(activity.get("estimated_cost", 0) or 0)
    return round(total, 2)


def deterministic_color(seed: str) -> str:
    return DEFAULT_PRESENCE_COLORS[
        sum(ord(char) for char in seed) % len(DEFAULT_PRESENCE_COLORS)
    ]


def get_session():
    with Session(engine) as session:
        yield session


# =============================================================================
# Exception handlers
# =============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    detail = (
        exc.detail
        if isinstance(exc.detail, dict)
        else {"message": str(exc.detail), "errors": {}}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": detail.get("message", "Request failed"),
            "errors": detail.get("errors", {}),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    errors: dict[str, list[str]] = defaultdict(list)
    for error in exc.errors():
        loc = [
            str(item)
            for item in error.get("loc", [])
            if item not in {"body", "query", "path"}
        ]
        field_name = ".".join(loc) or "non_field_errors"
        errors[field_name].append(error.get("msg", "Invalid value"))
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation failed",
            "errors": dict(errors),
        },
    )


# =============================================================================
# Database models / tables
# =============================================================================


class TimestampedModel(SQLModel):
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)


class User(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    avatar_url: str | None = None
    interests: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    home_district: str | None = None


class Location(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    district: str
    upazila: str | None = None
    type: str = Field(index=True)
    destination: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))


class CommunityContribution(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    user_id: str = Field(index=True)
    category: str = Field(index=True)
    name: str
    district: str = Field(index=True)
    upazila: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    price_range_min: float | None = None
    price_range_max: float | None = None
    amenities: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    tips: str | None = None
    photo_urls: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    embedded_video_urls: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: str = Field(default="pending_review")
    average_rating: float = Field(default=4.5)


class MediaAsset(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    resource_type: str
    url: str
    public_id: str
    context: str
    uploaded_by: str = Field(index=True)
    extra_data: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class GroupTrip(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    trip_name: str
    destination: str = Field(index=True)
    start_date: date
    end_date: date
    visibility: str = Field(index=True)
    description: str | None = None
    created_by: str = Field(index=True)
    invite_code: str = Field(index=True)
    cover_image_url: str | None = None


class GroupTripMember(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    group_trip_id: str = Field(index=True)
    user_id: str = Field(index=True)
    role: str = Field(default="Member")


class GeneratedItinerary(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    created_by: str = Field(index=True)
    destination: str = Field(index=True)
    duration_days: int
    budget: float
    travel_styles: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    interests: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    group_type: str | None = None
    prioritize_hidden_gems: bool = Field(default=False)
    estimated_total_cost: float = Field(default=0)
    days: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    request_context: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )


class SavedItinerary(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    generated_itinerary_id: str | None = Field(default=None, index=True)
    created_by: str = Field(index=True)
    trip_name: str
    destination: str = Field(index=True)
    duration_days: int
    budget_cap: float | None = None
    notes: str | None = None
    estimated_total_cost: float = Field(default=0)
    days: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    selected_activity_ids: list[str] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    manual_modifications: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )


class Accommodation(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    destination: str = Field(index=True)
    type: str = Field(index=True)
    price_per_night: float
    star_rating: float = Field(default=4.0)
    review_count: int = Field(default=0)
    amenities: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    distance_to_nearest_attraction_km: float = Field(default=0)
    nearest_attraction_name: str | None = None
    cover_photo_url: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    details: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    source_contribution_id: str | None = None


class NomadMetricRating(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    location_id: str = Field(index=True)
    user_id: str = Field(index=True)
    carrier_reports: list[dict[str, Any]] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    solo_female_safety_score: float | None = None
    solo_female_safety_tip: str | None = None
    digital_payment_reports: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    general_infrastructure: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )


class TripBudget(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    trip_id: str = Field(index=True)
    created_by: str = Field(index=True)
    total_budget: float
    category_allocations: dict[str, float] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )


class TripExpense(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    trip_id: str = Field(index=True)
    created_by: str = Field(index=True)
    amount: float
    category: str
    description: str | None = None
    expense_date: date
    receipt_photo_url: str | None = None


class ItineraryChatMessage(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    itinerary_id: str = Field(index=True)
    user_id: str = Field(index=True)
    user_message: str
    assistant_reply: str
    context_version: int = Field(default=1)
    suggested_changes: list[dict[str, Any]] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    updated_cost_summary: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    updated_itinerary_preview: list[dict[str, Any]] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    applied_change_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))


class GroupItineraryActivity(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    group_trip_id: str = Field(index=True)
    day: int
    title: str
    time: str | None = None
    location_id: str | None = None
    added_by: str = Field(index=True)
    status: str = Field(default="under_vote")
    vote_count: int = Field(default=0)


class GroupPresence(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    group_trip_id: str = Field(index=True)
    user_id: str = Field(index=True)
    status: str = Field(default="offline")
    role: str = Field(default="Member")
    editing_target: str | None = None
    presence_color: str = Field(default="teal")


class GroupPoll(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    group_trip_id: str = Field(index=True)
    question: str
    type: str
    deadline: datetime | None = None
    status: str = Field(default="active")
    created_by: str = Field(index=True)


class GroupPollOption(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    poll_id: str = Field(index=True)
    location_id: str | None = None
    label: str


class GroupPollVote(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    poll_id: str = Field(index=True)
    option_id: str = Field(index=True)
    user_id: str = Field(index=True)


class GroupActivityFeed(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    group_trip_id: str = Field(index=True)
    type: str
    message: str
    actor_user_id: str | None = None


class Notification(TimestampedModel, table=True):
    id: str = Field(primary_key=True)
    user_id: str = Field(index=True)
    type: str
    title: str
    message: str
    is_read: bool = Field(default=False)
    data_json: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


# =============================================================================
# Request schemas
# =============================================================================


class CommunityContributionCreate(SQLModel):
    category: str
    name: str
    district: str
    upazila: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    price_range_min: float | None = None
    price_range_max: float | None = None
    amenities: list[str] = Field(default_factory=list)
    tips: str | None = None
    photo_urls: list[str] = Field(default_factory=list)
    embedded_video_urls: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class CommunityContributionUpdate(SQLModel):
    category: str | None = None
    name: str | None = None
    district: str | None = None
    upazila: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    price_range_min: float | None = None
    price_range_max: float | None = None
    amenities: list[str] | None = None
    tips: str | None = None
    photo_urls: list[str] | None = None
    embedded_video_urls: list[str] | None = None
    tags: list[str] | None = None
    status: str | None = None


class GroupTripCreate(SQLModel):
    trip_name: str
    destination: str
    start_date: date
    end_date: date
    visibility: str
    description: str | None = None
    cover_image_url: str | None = None


class GroupTripUpdate(SQLModel):
    trip_name: str | None = None
    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    visibility: str | None = None
    description: str | None = None
    cover_image_url: str | None = None


class GroupJoinRequest(SQLModel):
    invite_code: str


class ItineraryGenerateRequest(SQLModel):
    destination: str
    duration_days: int
    budget: float
    travel_styles: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    group_type: str | None = None
    prioritize_hidden_gems: bool = False


class SaveItineraryRequest(SQLModel):
    generated_itinerary_id: str
    trip_name: str


class SavedItineraryUpdate(SQLModel):
    trip_name: str | None = None
    notes: str | None = None
    budget_cap: float | None = None
    days: list[dict[str, Any]] | None = None
    selected_activity_ids: list[str] | None = None
    manual_modifications: dict[str, Any] | None = None


class AccommodationTopPickRequest(SQLModel):
    destination: str
    budget_per_night: float
    planned_attraction_ids: list[str] = Field(default_factory=list)
    preferred_amenities: list[str] = Field(default_factory=list)
    trip_type: str | None = None


class NomadMetricsRatingCreate(SQLModel):
    carrier_reports: list[dict[str, Any]] = Field(default_factory=list)
    solo_female_safety_score: float | None = None
    solo_female_safety_tip: str | None = None
    digital_payment_reports: dict[str, Any] = Field(default_factory=dict)
    general_infrastructure: dict[str, Any] = Field(default_factory=dict)


class NomadMetricsRatingUpdate(SQLModel):
    carrier_reports: list[dict[str, Any]] | None = None
    solo_female_safety_score: float | None = None
    solo_female_safety_tip: str | None = None
    digital_payment_reports: dict[str, Any] | None = None
    general_infrastructure: dict[str, Any] | None = None


class BudgetCreateRequest(SQLModel):
    total_budget: float
    category_allocations: dict[str, float] = Field(default_factory=dict)


class ExpenseCreateRequest(SQLModel):
    amount: float
    category: str
    description: str | None = None
    expense_date: date
    receipt_photo_url: str | None = None


class ExpenseUpdateRequest(SQLModel):
    amount: float | None = None
    category: str | None = None
    description: str | None = None
    expense_date: date | None = None
    receipt_photo_url: str | None = None


class ItineraryChatRequest(SQLModel):
    message: str
    context_version: int = 1


class ItineraryChatApplyRequest(SQLModel):
    accepted_change_ids: list[str] = Field(default_factory=list)


class GroupActivityCreate(SQLModel):
    day: int
    title: str
    time: str | None = None
    location_id: str | None = None


class GroupActivityUpdate(SQLModel):
    day: int | None = None
    title: str | None = None
    time: str | None = None
    location_id: str | None = None
    status: str | None = None
    vote_count: int | None = None


class GroupPresenceUpsert(SQLModel):
    status: str = "online"
    role: str | None = None
    editing_target: str | None = None
    presence_color: str | None = None


class PollOptionCreate(SQLModel):
    location_id: str | None = None
    label: str


class PollCreate(SQLModel):
    question: str
    type: str
    deadline: datetime | None = None
    options: list[PollOptionCreate]


class PollVoteRequest(SQLModel):
    option_id: str


class MediaCreate(SQLModel):
    resource_type: str
    url: str
    public_id: str
    context: str
    extra_data: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Auth / lookup helpers
# =============================================================================


def get_current_user(
    session: Session = Depends(get_session),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
) -> User:
    user_id = x_user_id or DEMO_USER_ID
    user = session.get(User, user_id)
    if user:
        return user

    new_user = User(
        id=user_id,
        name="Demo User"
        if user_id == DEMO_USER_ID
        else user_id.replace("_", " ").title(),
        avatar_url=f"https://api.dicebear.com/8.x/initials/svg?seed={user_id}",
        interests=["Nature", "Food", "Photography"],
        home_district="Dhaka",
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


def get_or_404(session: Session, model: Any, object_id: str, label: str):
    obj = session.get(model, object_id)
    if not obj:
        api_error(404, f"{label} not found")
    return obj


def get_user_summary(session: Session, user_id: str) -> dict[str, Any]:
    user = session.get(User, user_id)
    if not user:
        return {"user_id": user_id, "name": user_id, "avatar_url": None}
    return {"user_id": user.id, "name": user.name, "avatar_url": user.avatar_url}


def get_group_member(
    session: Session, group_trip_id: str, user_id: str
) -> GroupTripMember | None:
    members = session.exec(
        select(GroupTripMember).where(GroupTripMember.group_trip_id == group_trip_id)
    ).all()
    return next((member for member in members if member.user_id == user_id), None)


def ensure_group_member(
    session: Session, group_trip_id: str, user_id: str
) -> GroupTripMember:
    member = get_group_member(session, group_trip_id, user_id)
    if not member:
        api_error(403, "You are not a member of this group trip")
    return member


def ensure_group_read_access(session: Session, trip: GroupTrip, user_id: str) -> None:
    if trip.visibility == "public":
        return
    if trip.created_by == user_id:
        return
    if get_group_member(session, trip.id, user_id):
        return
    api_error(403, "You do not have access to this group trip")


def ensure_owner(user_id: str, owner_id: str, label: str) -> None:
    if user_id != owner_id:
        api_error(403, f"You do not have permission to modify this {label}")


def add_group_feed(
    session: Session,
    group_trip_id: str,
    feed_type: str,
    message: str,
    actor_user_id: str | None = None,
) -> None:
    session.add(
        GroupActivityFeed(
            id=generate_id("feed"),
            group_trip_id=group_trip_id,
            type=feed_type,
            message=message,
            actor_user_id=actor_user_id,
        )
    )


def create_notification(
    session: Session,
    user_id: str,
    noti_type: str,
    title: str,
    message: str,
    data_json: dict[str, Any] | None = None,
) -> None:
    session.add(
        Notification(
            id=generate_id("noti"),
            user_id=user_id,
            type=noti_type,
            title=title,
            message=message,
            data_json=data_json or {},
        )
    )


# =============================================================================
# Serializers
# =============================================================================


def serialize_contribution_detail(item: CommunityContribution) -> dict[str, Any]:
    return {
        "id": item.id,
        "user_id": item.user_id,
        "category": item.category,
        "name": item.name,
        "district": item.district,
        "upazila": item.upazila,
        "address": item.address,
        "coordinates": {"latitude": item.latitude, "longitude": item.longitude},
        "price_range": {"min": item.price_range_min, "max": item.price_range_max},
        "amenities": item.amenities,
        "tips": item.tips,
        "photo_urls": item.photo_urls,
        "embedded_video_urls": item.embedded_video_urls,
        "tags": item.tags,
        "status": item.status,
        "average_rating": item.average_rating,
        "created_at": isoformat(item.created_at),
        "updated_at": isoformat(item.updated_at),
    }


def serialize_contribution_list_item(item: CommunityContribution) -> dict[str, Any]:
    return {
        "id": item.id,
        "name": item.name,
        "category": item.category,
        "district": item.district,
        "thumbnail_url": item.photo_urls[0] if item.photo_urls else None,
        "price_range": {"min": item.price_range_min, "max": item.price_range_max},
        "tags": item.tags,
        "average_rating": item.average_rating,
    }


def serialize_group_trip(
    session: Session, trip: GroupTrip, include_members: bool = False
) -> dict[str, Any]:
    members = session.exec(
        select(GroupTripMember).where(GroupTripMember.group_trip_id == trip.id)
    ).all()
    payload = {
        "id": trip.id,
        "trip_name": trip.trip_name,
        "destination": trip.destination,
        "start_date": trip.start_date.isoformat(),
        "end_date": trip.end_date.isoformat(),
        "visibility": trip.visibility,
        "description": trip.description,
        "created_by": trip.created_by,
        "invite_code": trip.invite_code,
        "invite_link": build_invite_link(trip.invite_code),
        "member_count": len(members),
        "cover_image_url": trip.cover_image_url,
        "created_at": isoformat(trip.created_at),
        "updated_at": isoformat(trip.updated_at),
    }
    if include_members:
        payload["members"] = [
            {
                "user_id": member.user_id,
                "role": member.role,
                "profile": get_user_summary(session, member.user_id),
                "joined_at": isoformat(member.created_at),
            }
            for member in members
        ]
    return payload


def serialize_saved_itinerary(item: SavedItinerary) -> dict[str, Any]:
    return {
        "id": item.id,
        "generated_itinerary_id": item.generated_itinerary_id,
        "trip_name": item.trip_name,
        "destination": item.destination,
        "duration_days": item.duration_days,
        "budget_cap": item.budget_cap,
        "notes": item.notes,
        "estimated_total_cost": item.estimated_total_cost,
        "days": item.days,
        "selected_activity_ids": item.selected_activity_ids,
        "manual_modifications": item.manual_modifications,
        "created_at": isoformat(item.created_at),
        "updated_at": isoformat(item.updated_at),
    }


def serialize_accommodation(
    item: Accommodation, detailed: bool = False
) -> dict[str, Any]:
    data = {
        "id": item.id,
        "name": item.name,
        "type": item.type,
        "destination": item.destination,
        "price_per_night": item.price_per_night,
        "star_rating": item.star_rating,
        "review_count": item.review_count,
        "amenities": item.amenities,
        "distance_to_nearest_attraction_km": item.distance_to_nearest_attraction_km,
        "nearest_attraction_name": item.nearest_attraction_name,
        "cover_photo_url": item.cover_photo_url,
        "coordinates": {"latitude": item.latitude, "longitude": item.longitude},
    }
    if detailed:
        data["details"] = item.details
        data["source_contribution_id"] = item.source_contribution_id
        data["created_at"] = isoformat(item.created_at)
    return data


def serialize_nomad_rating(session: Session, item: NomadMetricRating) -> dict[str, Any]:
    return {
        "id": item.id,
        "user": get_user_summary(session, item.user_id),
        "carrier_reports": item.carrier_reports,
        "solo_female_safety_score": item.solo_female_safety_score,
        "solo_female_safety_tip": item.solo_female_safety_tip,
        "digital_payment_reports": item.digital_payment_reports,
        "general_infrastructure": item.general_infrastructure,
        "created_at": isoformat(item.created_at),
        "updated_at": isoformat(item.updated_at),
    }


def serialize_expense(item: TripExpense) -> dict[str, Any]:
    return {
        "expense_id": item.id,
        "amount": item.amount,
        "category": item.category,
        "description": item.description,
        "expense_date": item.expense_date.isoformat(),
        "receipt_photo_url": item.receipt_photo_url,
        "created_by": item.created_by,
        "created_at": isoformat(item.created_at),
        "updated_at": isoformat(item.updated_at),
    }


def serialize_group_activity(
    session: Session, item: GroupItineraryActivity
) -> dict[str, Any]:
    profile = get_user_summary(session, item.added_by)
    return {
        "activity_id": item.id,
        "title": item.title,
        "time": item.time,
        "location_id": item.location_id,
        "added_by": {"user_id": profile["user_id"], "name": profile["name"]},
        "vote_count": item.vote_count,
        "status": item.status,
    }


def poll_is_active(poll: GroupPoll) -> bool:
    if poll.status == "closed":
        return False
    if poll.deadline and poll.deadline < utcnow():
        return False
    return True


def serialize_poll(session: Session, poll: GroupPoll) -> dict[str, Any]:
    options = session.exec(
        select(GroupPollOption).where(GroupPollOption.poll_id == poll.id)
    ).all()
    votes = session.exec(
        select(GroupPollVote).where(GroupPollVote.poll_id == poll.id)
    ).all()
    vote_counts = Counter(vote.option_id for vote in votes)
    status_value = "active" if poll_is_active(poll) else "closed"
    return {
        "poll_id": poll.id,
        "question": poll.question,
        "type": poll.type,
        "deadline": isoformat(poll.deadline),
        "status": status_value,
        "options": [
            {
                "option_id": option.id,
                "location_id": option.location_id,
                "label": option.label,
                "vote_count": vote_counts.get(option.id, 0),
            }
            for option in options
        ],
    }


def serialize_feed_item(item: GroupActivityFeed) -> dict[str, Any]:
    return {
        "id": item.id,
        "type": item.type,
        "message": item.message,
        "created_at": isoformat(item.created_at),
    }


def serialize_notification(item: Notification) -> dict[str, Any]:
    return {
        "id": item.id,
        "type": item.type,
        "title": item.title,
        "message": item.message,
        "is_read": item.is_read,
        "data": item.data_json,
        "created_at": isoformat(item.created_at),
    }


# =============================================================================
# Heuristic business logic
# =============================================================================


def upsert_location_from_contribution(
    session: Session, contribution: CommunityContribution
) -> None:
    locations = session.exec(select(Location)).all()
    existing = next(
        (
            item
            for item in locations
            if normalize(item.name) == normalize(contribution.name)
            and normalize(item.district) == normalize(contribution.district)
        ),
        None,
    )
    if existing:
        if contribution.latitude is not None:
            existing.latitude = contribution.latitude
        if contribution.longitude is not None:
            existing.longitude = contribution.longitude
        existing.tags = list(set(existing.tags + contribution.tags))
        touch(existing)
        session.add(existing)
        return

    session.add(
        Location(
            id=generate_id("loc"),
            name=contribution.name,
            district=contribution.district,
            upazila=contribution.upazila,
            type=contribution.category,
            destination=contribution.district,
            latitude=contribution.latitude,
            longitude=contribution.longitude,
            tags=contribution.tags,
        )
    )


def maybe_create_accommodation_from_contribution(
    session: Session, contribution: CommunityContribution
) -> None:
    if contribution.category not in {"hotel", "guesthouse", "homestay"}:
        return

    all_items = session.exec(select(Accommodation)).all()
    already_exists = next(
        (item for item in all_items if item.source_contribution_id == contribution.id),
        None,
    )
    if already_exists:
        return

    session.add(
        Accommodation(
            id=generate_id("acc"),
            name=contribution.name,
            destination=contribution.district,
            type=contribution.category.title(),
            price_per_night=float(
                contribution.price_range_max or contribution.price_range_min or 1500
            ),
            star_rating=4.0,
            review_count=12,
            amenities=contribution.amenities,
            distance_to_nearest_attraction_km=1.5,
            nearest_attraction_name=contribution.district,
            cover_photo_url=contribution.photo_urls[0]
            if contribution.photo_urls
            else None,
            latitude=contribution.latitude,
            longitude=contribution.longitude,
            details={"address": contribution.address, "tips": contribution.tips},
            source_contribution_id=contribution.id,
        )
    )


def generate_itinerary_days(
    session: Session, payload: ItineraryGenerateRequest
) -> list[dict[str, Any]]:
    all_locations = session.exec(select(Location)).all()
    matching_locations = [
        item
        for item in all_locations
        if text_match(
            payload.destination,
            item.name,
            item.destination,
            item.district,
            item.upazila,
        )
    ]
    if not matching_locations:
        matching_locations = all_locations[:3]

    all_contributions = session.exec(select(CommunityContribution)).all()
    matching_contributions = [
        item
        for item in all_contributions
        if text_match(payload.destination, item.name, item.district, item.upazila)
    ]

    hidden_gems = [item for item in matching_contributions if "Hidden Gem" in item.tags]
    interest_pool = payload.interests or ["Nature", "Food", "Culture"]

    days: list[dict[str, Any]] = []
    estimated_daily_cap = max(payload.budget / max(payload.duration_days, 1), 1000)

    for day_number in range(1, payload.duration_days + 1):
        interest = interest_pool[(day_number - 1) % len(interest_pool)]
        location = (
            matching_locations[(day_number - 1) % max(len(matching_locations), 1)]
            if matching_locations
            else None
        )
        chosen_hidden = (
            hidden_gems[(day_number - 1) % len(hidden_gems)] if hidden_gems else None
        )

        activities = [
            {
                "time": "08:00",
                "title": f"Breakfast and local start in {payload.destination}",
                "description": f"Ease into Day {day_number} with a simple breakfast and route planning.",
                "estimated_cost": round(min(estimated_daily_cap * 0.12, 250), 2),
                "location_id": location.id if location else None,
                "tags": ["Food"],
            }
        ]

        if chosen_hidden and payload.prioritize_hidden_gems:
            activities.append(
                {
                    "time": "11:00",
                    "title": f"Visit {chosen_hidden.name}",
                    "description": chosen_hidden.tips
                    or "Explore one of the area's community-favored hidden gems.",
                    "estimated_cost": round(min(estimated_daily_cap * 0.28, 900), 2),
                    "location_id": None,
                    "tags": [interest, "Hidden Gem"],
                    "local_cultural_insight": "Ask local guides about the best seasonal timing before you go.",
                }
            )
        elif location:
            activities.append(
                {
                    "time": "11:00",
                    "title": f"Explore {location.name}",
                    "description": f"Spend the late morning around {location.name}.",
                    "estimated_cost": round(min(estimated_daily_cap * 0.25, 850), 2),
                    "location_id": location.id,
                    "tags": [interest],
                }
            )

        activities.append(
            {
                "time": "16:30",
                "title": f"{interest} stop and relaxed evening",
                "description": f"Wrap the day with a lighter {interest.lower()} activity and dinner.",
                "estimated_cost": round(min(estimated_daily_cap * 0.2, 600), 2),
                "location_id": location.id if location else None,
                "tags": [interest],
            }
        )

        days.append(
            {"day": day_number, "theme": f"{interest} focus", "activities": activities}
        )

    return days


def build_nomad_metrics(
    location: Location, ratings: list[NomadMetricRating]
) -> dict[str, Any]:
    carrier_counters: dict[str, dict[str, int]] = defaultdict(
        lambda: {"no_signal_votes": 0, "2g_votes": 0, "3g_votes": 0, "4g_votes": 0}
    )
    signal_key_map = {
        "no signal": "no_signal_votes",
        "2g": "2g_votes",
        "3g": "3g_votes",
        "4g": "4g_votes",
    }

    safety_scores: list[float] = []
    safety_tips: list[str] = []
    payment_votes: dict[str, list[str]] = {"bkash": [], "nagad": [], "rocket": []}
    infra_values: dict[str, list[float]] = {
        "electricity_reliability": [],
        "clean_water_access": [],
        "road_quality": [],
    }

    for rating in ratings:
        for report in rating.carrier_reports:
            carrier = report.get("carrier", "Unknown")
            signal = normalize(report.get("signal"))
            vote_key = signal_key_map.get(signal, "no_signal_votes")
            carrier_counters[carrier][vote_key] += 1

        if rating.solo_female_safety_score is not None:
            safety_scores.append(float(rating.solo_female_safety_score))
        if rating.solo_female_safety_tip:
            safety_tips.append(rating.solo_female_safety_tip)

        for method in payment_votes:
            status_value = str(rating.digital_payment_reports.get(method, "")).strip()
            if status_value:
                payment_votes[method].append(status_value)

        for key in infra_values:
            value = rating.general_infrastructure.get(key)
            if value is not None:
                infra_values[key].append(float(value))

    network_connectivity = []
    for carrier, counts in carrier_counters.items():
        dominant_key = (
            max(counts.items(), key=lambda item: item[1])[0]
            if sum(counts.values())
            else "no_signal_votes"
        )
        label_map = {
            "no_signal_votes": "No Signal",
            "2g_votes": "2G",
            "3g_votes": "3G",
            "4g_votes": "4G",
        }
        network_connectivity.append(
            {
                "carrier": carrier,
                "signal_levels": counts,
                "dominant_signal": label_map[dominant_key],
            }
        )

    payment_summary = {}
    for method, statuses in payment_votes.items():
        if statuses:
            common_status = Counter(statuses).most_common(1)[0][0]
            availability_percent = round(
                (statuses.count("Available") * 100 + statuses.count("Limited") * 50)
                / len(statuses),
                0,
            )
        else:
            common_status = "Unavailable"
            availability_percent = 0
        payment_summary[method] = {
            "status": common_status,
            "availability_percent": availability_percent,
        }

    infra_summary = {
        key: round(sum(values) / len(values), 1) if values else 0
        for key, values in infra_values.items()
    }

    return {
        "location_id": location.id,
        "location_name": location.name,
        "network_connectivity": network_connectivity,
        "solo_female_safety": {
            "score": round(sum(safety_scores) / len(safety_scores), 1)
            if safety_scores
            else 0,
            "rating_count": len(safety_scores),
            "top_tips": list(dict.fromkeys(safety_tips))[:3],
        },
        "digital_payments": payment_summary,
        "general_infrastructure": infra_summary,
    }


def build_nomad_map(session: Session, location: Location, layer: str) -> dict[str, Any]:
    if layer not in {"network", "safety", "payments"}:
        api_error(
            422,
            "Validation failed",
            {"layer": ["Must be one of: network, safety, payments"]},
        )

    lat = location.latitude or 23.8103
    lng = location.longitude or 90.4125

    layer_meta = {
        "network": ("Strong mobile coverage zone", "#2A9D8F"),
        "safety": ("Safer movement corridor", "#264653"),
        "payments": ("Digital payment availability", "#E9C46A"),
    }
    label, color = layer_meta[layer]

    accommodations = session.exec(select(Accommodation)).all()
    contributions = session.exec(select(CommunityContribution)).all()

    candidate_pins = []
    for item in accommodations:
        if normalize(item.destination) == normalize(location.district):
            candidate_pins.append(
                {
                    "poi_id": item.id,
                    "name": item.name,
                    "latitude": item.latitude,
                    "longitude": item.longitude,
                    "popup_summary": f"{item.type} • {item.star_rating}★ • {', '.join(item.amenities[:2])}",
                }
            )
    for item in contributions:
        if normalize(item.district) == normalize(location.district):
            candidate_pins.append(
                {
                    "poi_id": item.id,
                    "name": item.name,
                    "latitude": item.latitude,
                    "longitude": item.longitude,
                    "popup_summary": f"{item.category.title()} contribution • {item.status.replace('_', ' ')}",
                }
            )

    candidate_pins = [
        pin
        for pin in candidate_pins
        if pin["latitude"] is not None and pin["longitude"] is not None
    ][:5]

    return {
        "location_id": location.id,
        "layer": layer,
        "overlays": [
            {
                "zone_id": generate_id("zone"),
                "label": label,
                "color": color,
                "polygon": [
                    [round(lat + 0.001, 6), round(lng + 0.001, 6)],
                    [round(lat + 0.002, 6), round(lng + 0.003, 6)],
                    [round(lat - 0.001, 6), round(lng + 0.002, 6)],
                ],
            }
        ],
        "pins": candidate_pins,
    }


def compute_budget_summary(session: Session, trip_id: str) -> dict[str, Any]:
    budget = next(
        (
            item
            for item in session.exec(select(TripBudget)).all()
            if item.trip_id == trip_id
        ),
        None,
    )
    if not budget:
        api_error(404, "Budget not found")
    assert budget is not None

    expenses = [
        item
        for item in session.exec(select(TripExpense)).all()
        if item.trip_id == trip_id
    ]
    total_spent = round(sum(item.amount for item in expenses), 2)
    remaining_budget = round(budget.total_budget - total_spent, 2)
    spent_percentage = (
        round((total_spent / budget.total_budget) * 100, 0)
        if budget.total_budget
        else 0
    )

    alerts = []
    if spent_percentage >= 100:
        alerts.append(
            {"type": "danger", "message": "You've exceeded or fully used your budget."}
        )
    elif spent_percentage >= 80:
        alerts.append(
            {
                "type": "warning",
                "message": f"You've used {int(spent_percentage)}% of your budget.",
            }
        )

    category_breakdown: dict[str, float] = defaultdict(float)
    daily_totals: dict[str, float] = defaultdict(float)
    for expense in expenses:
        category_breakdown[expense.category] += expense.amount
        daily_totals[expense.expense_date.isoformat()] += expense.amount

    days_with_spend = max(len(daily_totals), 1)
    daily_average_spending = round(total_spent / days_with_spend, 2)

    matching_trip = session.get(GroupTrip, trip_id)
    if matching_trip:
        duration_days = max(
            (matching_trip.end_date - matching_trip.start_date).days + 1, 1
        )
    else:
        duration_days = days_with_spend

    projected_total_spending = round(daily_average_spending * duration_days, 2)

    if spent_percentage < 60:
        status_color = "green"
    elif spent_percentage < 90:
        status_color = "amber"
    else:
        status_color = "red"

    return {
        "trip_id": trip_id,
        "total_budget": budget.total_budget,
        "total_spent": total_spent,
        "remaining_budget": remaining_budget,
        "spent_percentage": spent_percentage,
        "status_color": status_color,
        "alerts": alerts,
        "category_breakdown": {
            key: round(value, 2) for key, value in category_breakdown.items()
        },
        "daily_average_spending": daily_average_spending,
        "projected_total_spending": projected_total_spending,
    }


def maybe_emit_budget_notifications(
    session: Session, budget: TripBudget, summary: dict[str, Any]
) -> None:
    thresholds = [80, 100]
    existing = [
        n
        for n in session.exec(select(Notification)).all()
        if n.user_id == budget.created_by
    ]
    for threshold in thresholds:
        already_sent = any(
            n.type == f"budget_threshold_{threshold}"
            and n.data_json.get("trip_id") == budget.trip_id
            for n in existing
        )
        if summary["spent_percentage"] >= threshold and not already_sent:
            create_notification(
                session,
                budget.created_by,
                f"budget_threshold_{threshold}",
                "Budget alert",
                f"Trip {budget.trip_id} has reached {int(summary['spent_percentage'])}% of the budget.",
                {"trip_id": budget.trip_id, "threshold": threshold},
            )


def build_chat_refinement(itinerary: SavedItinerary, message: str) -> dict[str, Any]:
    lowered = message.lower()
    updated_days = deepcopy(itinerary.days)
    suggested_changes: list[dict[str, Any]] = []
    preview_days: list[dict[str, Any]] = []
    reply_parts: list[str] = []

    previous_total = itinerary.estimated_total_cost or calculate_itinerary_total(
        itinerary.days
    )

    if "nature" in lowered:
        target_day = 2 if len(updated_days) >= 2 else 1
        for day in updated_days:
            if day.get("day") == target_day:
                new_activity = {
                    "time": "16:00",
                    "title": "Short forest trail walk",
                    "description": "A low-cost, nature-heavy stop added from heuristic chat refinement.",
                    "estimated_cost": 0,
                    "tags": ["Nature"],
                }
                day.setdefault("activities", []).append(new_activity)
                change_id = generate_id("chg")
                suggested_changes.append(
                    {
                        "id": change_id,
                        "type": "add_activity",
                        "day": target_day,
                        "new_activity": new_activity["title"],
                    }
                )
                preview_days.append(
                    {"day": target_day, "activities": day["activities"]}
                )
                reply_parts.append(
                    f"I added a more nature-focused stop on Day {target_day}."
                )
                break

    budget_target_match = re.search(r"under\s+(\d+)", lowered)
    if budget_target_match:
        budget_target = float(budget_target_match.group(1))
        most_expensive: tuple[dict[str, Any], dict[str, Any]] | None = None
        for day in updated_days:
            for activity in day.get("activities", []):
                cost = float(activity.get("estimated_cost", 0) or 0)
                if most_expensive is None or cost > float(
                    most_expensive[1].get("estimated_cost", 0) or 0
                ):
                    most_expensive = (day, activity)

        if most_expensive and previous_total > budget_target:
            day, activity = most_expensive
            old_title = activity.get("title", "Expensive activity")
            old_cost = float(activity.get("estimated_cost", 0) or 0)
            activity["title"] = "Local food market dinner"
            activity["description"] = (
                "A lower-cost swap suggested by the itinerary assistant."
            )
            activity["estimated_cost"] = min(old_cost, 250)
            change_id = generate_id("chg")
            suggested_changes.append(
                {
                    "id": change_id,
                    "type": "replace_activity",
                    "day": day.get("day"),
                    "old_activity": old_title,
                    "new_activity": activity["title"],
                }
            )
            preview_days.append({"day": day["day"], "activities": day["activities"]})
            reply_parts.append(
                f"I replaced one higher-cost stop to help keep the trip under {int(budget_target)} taka."
            )

    if not suggested_changes:
        reply_parts.append(
            "I reviewed the itinerary and have a conservative recommendation without changing the plan structure yet."
        )

    unique_preview = {item["day"]: item for item in preview_days}
    preview_list = list(unique_preview.values())
    new_total = calculate_itinerary_total(updated_days)

    return {
        "reply": " ".join(reply_parts),
        "suggested_changes": suggested_changes,
        "updated_cost_summary": {
            "previous_total": previous_total,
            "new_total": new_total,
        },
        "updated_itinerary_preview": preview_list,
    }


def build_group_itinerary(session: Session, group_trip_id: str) -> dict[str, Any]:
    activities = session.exec(
        select(GroupItineraryActivity).where(
            GroupItineraryActivity.group_trip_id == group_trip_id
        )
    ).all()
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for activity in sorted(activities, key=lambda item: (item.day, item.time or "")):
        grouped[activity.day].append(serialize_group_activity(session, activity))
    return {
        "group_trip_id": group_trip_id,
        "days": [
            {"day": day, "activities": grouped[day]} for day in sorted(grouped.keys())
        ],
    }


# =============================================================================
# Startup / seed data
# =============================================================================


def seed_demo_data(session: Session) -> None:
    if session.exec(select(User)).first():
        return

    users = [
        User(
            id=DEMO_USER_ID,
            name="Nafis",
            avatar_url="https://example.com/avatar/nafis.jpg",
            interests=["Photography", "Food", "Nature"],
            home_district="Dhaka",
        ),
        User(
            id="user_88",
            name="Rafi",
            avatar_url="https://example.com/avatar/rafi.jpg",
            interests=["Photography", "Adventure", "Nature"],
            home_district="Sylhet",
        ),
        User(
            id="user_91",
            name="Tania",
            avatar_url="https://example.com/avatar/tania.jpg",
            interests=["Adventure", "Hiking", "Food"],
            home_district="Chattogram",
        ),
    ]
    session.add_all(users)

    locations = [
        Location(
            id="loc_5002",
            name="Ratargul Swamp Forest",
            district="Sylhet",
            upazila="Gowainghat",
            type="attraction",
            destination="Sylhet",
            latitude=25.0013,
            longitude=91.9368,
            tags=["Hidden Gem"],
        ),
        Location(
            id="loc_7001",
            name="Sajek Valley",
            district="Rangamati",
            upazila="Baghaichhari",
            type="destination",
            destination="Sajek Valley",
            latitude=23.3811,
            longitude=92.2934,
            tags=["Trending"],
        ),
        Location(
            id="loc_7002",
            name="Konglak Hill",
            district="Rangamati",
            upazila="Baghaichhari",
            type="attraction",
            destination="Sajek Valley",
            latitude=23.3798,
            longitude=92.2919,
            tags=["Trending"],
        ),
        Location(
            id="loc_8004",
            name="Local Bamboo Restaurant",
            district="Rangamati",
            upazila="Baghaichhari",
            type="restaurant",
            destination="Sajek Valley",
            latitude=23.3805,
            longitude=92.2923,
            tags=[],
        ),
        Location(
            id="loc_9001",
            name="Niladri Lake",
            district="Sunamganj",
            upazila="Tahirpur",
            type="attraction",
            destination="Sunamganj",
            latitude=25.1142,
            longitude=91.0023,
            tags=["Hidden Gem"],
        ),
    ]
    session.add_all(locations)

    contributions = [
        CommunityContribution(
            id="contrib_101",
            user_id=DEMO_USER_ID,
            category="attraction",
            name="Niladri Lake",
            district="Sunamganj",
            upazila="Tahirpur",
            address="Tekerghat, Tahirpur, Sunamganj",
            latitude=25.1142,
            longitude=91.0023,
            price_range_min=100,
            price_range_max=800,
            amenities=["Boat Ride", "Parking", "Food Stalls"],
            tips="Visit early morning for the best light and fewer crowds.",
            photo_urls=["https://res.cloudinary.com/demo/image/upload/v1/niladri1.jpg"],
            embedded_video_urls=["https://www.youtube.com/watch?v=abcd1234"],
            tags=["Hidden Gem"],
            average_rating=4.7,
        ),
        CommunityContribution(
            id="contrib_102",
            user_id="user_88",
            category="restaurant",
            name="Panshi Restaurant",
            district="Sylhet",
            upazila="Sylhet Sadar",
            address="Zindabazar, Sylhet",
            latitude=24.8949,
            longitude=91.8687,
            price_range_min=150,
            price_range_max=600,
            amenities=["Local Food", "Seating"],
            tips="Try their local breakfast set before a long day trip.",
            photo_urls=["https://res.cloudinary.com/demo/image/upload/v1/panshi.jpg"],
            embedded_video_urls=[],
            tags=["Trending"],
            average_rating=4.4,
        ),
        CommunityContribution(
            id="contrib_103",
            user_id="user_91",
            category="homestay",
            name="Hilltop Homestay",
            district="Rangamati",
            upazila="Baghaichhari",
            address="Near Konglak Hill, Sajek Valley",
            latitude=23.3798,
            longitude=92.2919,
            price_range_min=2200,
            price_range_max=2800,
            amenities=["WiFi", "Parking", "Local Meals"],
            tips="Request a hill-facing room for sunrise views.",
            photo_urls=["https://res.cloudinary.com/demo/image/upload/v1/hilltop.jpg"],
            embedded_video_urls=[],
            tags=["Trending"],
            average_rating=4.3,
        ),
    ]
    session.add_all(contributions)

    accommodations = [
        Accommodation(
            id="acc_401",
            name="Megh Valley Resort",
            destination="Sajek Valley",
            type="Hotel",
            price_per_night=4200,
            star_rating=4.5,
            review_count=128,
            amenities=["WiFi", "Hot Water", "Restaurant"],
            distance_to_nearest_attraction_km=1.2,
            nearest_attraction_name="Sajek Valley Viewpoint",
            cover_photo_url="https://res.cloudinary.com/demo/image/upload/v1/megh-valley.jpg",
            latitude=23.3811,
            longitude=92.2934,
            details={
                "rooms": 18,
                "check_in": "12:00",
                "note": "Popular among friend groups.",
            },
        ),
        Accommodation(
            id="acc_402",
            name="Hilltop Homestay",
            destination="Sajek Valley",
            type="Homestay",
            price_per_night=2500,
            star_rating=4.3,
            review_count=54,
            amenities=["WiFi", "Parking", "Local Meals"],
            distance_to_nearest_attraction_km=0.8,
            nearest_attraction_name="Konglak Hill",
            cover_photo_url="https://res.cloudinary.com/demo/image/upload/v1/hilltop.jpg",
            latitude=23.3798,
            longitude=92.2919,
            details={"host": "Local family stay", "check_in": "11:00"},
            source_contribution_id="contrib_103",
        ),
        Accommodation(
            id="acc_403",
            name="Tea Garden Eco Lodge",
            destination="Sylhet",
            type="Hotel",
            price_per_night=3200,
            star_rating=4.4,
            review_count=37,
            amenities=["WiFi", "Hot Water", "Breakfast"],
            distance_to_nearest_attraction_km=2.1,
            nearest_attraction_name="Ratargul Swamp Forest",
            cover_photo_url="https://res.cloudinary.com/demo/image/upload/v1/tea-lodge.jpg",
            latitude=24.9264,
            longitude=91.8823,
            details={"eco_friendly": True},
        ),
    ]
    session.add_all(accommodations)

    group_trip = GroupTrip(
        id="group_201",
        trip_name="Sajek Friends Tour",
        destination="Sajek Valley",
        start_date=date(2025, 6, 10),
        end_date=date(2025, 6, 14),
        visibility="public",
        description="A 4-night relaxed trip with nature, food, and photography focus.",
        created_by=DEMO_USER_ID,
        invite_code="SAJEK2025XYZ",
        cover_image_url="https://res.cloudinary.com/demo/image/upload/v1/sajek-cover.jpg",
    )
    session.add(group_trip)

    session.add_all(
        [
            GroupTripMember(
                id=generate_id("member"),
                group_trip_id="group_201",
                user_id=DEMO_USER_ID,
                role="Organizer",
            ),
            GroupTripMember(
                id=generate_id("member"),
                group_trip_id="group_201",
                user_id="user_88",
                role="Member",
            ),
        ]
    )

    generated_days = [
        {
            "day": 1,
            "theme": "Nature and Local Food",
            "activities": [
                {
                    "time": "08:00",
                    "title": "Breakfast at Panshi Restaurant",
                    "description": "Try local Sylheti breakfast items before starting the day.",
                    "estimated_cost": 180,
                    "location_id": "loc_8004",
                    "tags": ["Food"],
                },
                {
                    "time": "11:00",
                    "title": "Visit Ratargul Swamp Forest",
                    "description": "Boat tour through the freshwater swamp forest.",
                    "estimated_cost": 850,
                    "location_id": "loc_5002",
                    "tags": ["Nature", "Hidden Gem"],
                    "local_cultural_insight": "Local boatmen often share stories about seasonal changes and water levels.",
                },
            ],
        }
    ]

    session.add(
        GeneratedItinerary(
            id="iti_301",
            created_by=DEMO_USER_ID,
            destination="Sylhet",
            duration_days=3,
            budget=12000,
            travel_styles=["Budget", "Adventure"],
            interests=["Nature", "Photography", "Food"],
            group_type="Friends",
            prioritize_hidden_gems=True,
            estimated_total_cost=10950,
            days=generated_days,
            request_context={
                "destination": "Sylhet",
                "duration_days": 3,
                "budget": 12000,
                "travel_styles": ["Budget", "Adventure"],
                "interests": ["Nature", "Photography", "Food"],
                "group_type": "Friends",
                "prioritize_hidden_gems": True,
            },
        )
    )

    session.add(
        SavedItinerary(
            id="saved_301",
            generated_itinerary_id="iti_301",
            created_by=DEMO_USER_ID,
            trip_name="Sylhet Adventure Plan",
            destination="Sylhet",
            duration_days=3,
            budget_cap=12000,
            notes="Demo saved itinerary",
            estimated_total_cost=10950,
            days=generated_days,
        )
    )

    session.add_all(
        [
            GroupItineraryActivity(
                id="act_1",
                group_trip_id="group_201",
                day=1,
                title="Reach Sajek and check in",
                time="10:00",
                location_id="loc_7001",
                added_by=DEMO_USER_ID,
                status="confirmed",
                vote_count=4,
            ),
            GroupItineraryActivity(
                id="act_2",
                group_trip_id="group_201",
                day=1,
                title="Sunset at Konglak Hill",
                time="17:00",
                location_id="loc_7002",
                added_by="user_88",
                status="under_vote",
                vote_count=3,
            ),
        ]
    )

    session.add_all(
        [
            GroupPresence(
                id=generate_id("presence"),
                group_trip_id="group_201",
                user_id=DEMO_USER_ID,
                status="online",
                role="Organizer",
                editing_target="Day 2 Activity act_8",
                presence_color="teal",
            ),
            GroupPresence(
                id=generate_id("presence"),
                group_trip_id="group_201",
                user_id="user_88",
                status="offline",
                role="Member",
                editing_target=None,
                presence_color="purple",
            ),
        ]
    )

    poll = GroupPoll(
        id="poll_11",
        group_trip_id="group_201",
        question="Where should we eat dinner on Day 2?",
        type="restaurant",
        deadline=datetime(2026, 6, 9, 20, 0, tzinfo=timezone.utc),
        status="active",
        created_by=DEMO_USER_ID,
    )
    session.add(poll)
    session.add_all(
        [
            GroupPollOption(
                id="opt_1",
                poll_id="poll_11",
                location_id="loc_100",
                label="Paharika Restaurant",
            ),
            GroupPollOption(
                id="opt_2",
                poll_id="poll_11",
                location_id="loc_101",
                label="Megh Cabin BBQ",
            ),
            GroupPollOption(
                id="opt_3",
                poll_id="poll_11",
                location_id="loc_102",
                label="Hill View Restaurant",
            ),
        ]
    )

    session.add_all(
        [
            GroupActivityFeed(
                id="feed_1",
                group_trip_id="group_201",
                type="activity_added",
                message="Rima added Ratargul Swamp Forest to Day 3",
                actor_user_id="user_88",
            ),
            GroupActivityFeed(
                id="feed_2",
                group_trip_id="group_201",
                type="poll_created",
                message="New poll: Day 2 dinner spot?",
                actor_user_id=DEMO_USER_ID,
            ),
        ]
    )

    session.add(
        NomadMetricRating(
            id=generate_id("rating"),
            location_id="loc_5002",
            user_id=DEMO_USER_ID,
            carrier_reports=[
                {"carrier": "Grameenphone", "signal": "3G"},
                {"carrier": "Robi", "signal": "No Signal"},
            ],
            solo_female_safety_score=4.0,
            solo_female_safety_tip="Daytime felt safe, but public transport gets sparse after evening.",
            digital_payment_reports={
                "bkash": "Available",
                "nagad": "Limited",
                "rocket": "Unavailable",
            },
            general_infrastructure={
                "electricity_reliability": 3,
                "clean_water_access": 4,
                "road_quality": 2,
            },
        )
    )

    session.add(
        TripBudget(
            id=generate_id("budget"),
            trip_id="group_201",
            created_by=DEMO_USER_ID,
            total_budget=20000,
            category_allocations={
                "accommodation": 7000,
                "food": 4000,
                "transport": 5000,
                "attractions": 2500,
                "shopping": 1000,
                "other": 500,
            },
        )
    )
    session.add_all(
        [
            TripExpense(
                id="exp_1001",
                trip_id="group_201",
                created_by=DEMO_USER_ID,
                amount=850,
                category="transport",
                description="CNG fare from station to resort",
                expense_date=date(2025, 6, 11),
                receipt_photo_url="https://res.cloudinary.com/demo/image/upload/v1/receipt123.jpg",
            ),
            TripExpense(
                id="exp_1002",
                trip_id="group_201",
                created_by=DEMO_USER_ID,
                amount=2600,
                category="food",
                description="Meals for Day 1",
                expense_date=date(2025, 6, 10),
                receipt_photo_url=None,
            ),
        ]
    )

    session.add(
        Notification(
            id=generate_id("noti"),
            user_id=DEMO_USER_ID,
            type="invite_join",
            title="Group update",
            message="Rafi joined your Sajek Friends Tour.",
            data_json={"group_trip_id": "group_201"},
        )
    )

    session.commit()


@app.on_event("startup")
def on_startup() -> None:
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed_demo_data(session)


# =============================================================================
# Shared supporting APIs
# =============================================================================


@app.post(f"{API_PREFIX}/media", status_code=status.HTTP_201_CREATED)
def upload_media_metadata(
    payload: MediaCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    asset = MediaAsset(
        id=generate_id("media"),
        resource_type=payload.resource_type,
        url=payload.url,
        public_id=payload.public_id,
        context=payload.context,
        uploaded_by=current_user.id,
        extra_data=payload.extra_data,
    )
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return success_response(
        "Media metadata stored successfully",
        {
            "id": asset.id,
            "resource_type": asset.resource_type,
            "url": asset.url,
            "public_id": asset.public_id,
            "context": asset.context,
            "uploaded_by": asset.uploaded_by,
            "created_at": isoformat(asset.created_at),
        },
    )


@app.get(f"{API_PREFIX}/locations/search")
def search_locations(
    q: str = Query(..., min_length=1),
    session: Session = Depends(get_session),
):
    locations = session.exec(select(Location)).all()
    matches = [
        item
        for item in locations
        if text_match(
            q, item.name, item.district, item.upazila, item.type, item.destination
        )
    ]
    return success_response(
        "Locations fetched successfully",
        [
            {
                "id": item.id,
                "name": item.name,
                "district": item.district,
                "type": item.type,
            }
            for item in matches[:20]
        ],
    )


@app.get(f"{API_PREFIX}/notifications")
def get_notifications(
    unread_only: bool = Query(False),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    notifications = [
        item
        for item in session.exec(select(Notification)).all()
        if item.user_id == current_user.id
    ]
    if unread_only:
        notifications = [item for item in notifications if not item.is_read]
    notifications.sort(key=lambda item: item.created_at, reverse=True)
    return success_response(
        "Notifications fetched successfully",
        [serialize_notification(item) for item in notifications],
    )


# =============================================================================
# Member-1 APIs
# =============================================================================
# Feature 1: Community Data Contribution Page
# =============================================================================


@app.post(f"{API_PREFIX}/community/contributions", status_code=status.HTTP_201_CREATED)
def create_community_contribution(
    payload: CommunityContributionCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if payload.category not in COMMUNITY_CATEGORIES:
        api_error(
            422,
            "Validation failed",
            {
                "category": [
                    f"Must be one of: {', '.join(sorted(COMMUNITY_CATEGORIES))}"
                ]
            },
        )
    ensure_tags(payload.tags)
    ensure_price_range(payload.price_range_min, payload.price_range_max)

    contribution = CommunityContribution(
        id=generate_id("contrib"),
        user_id=current_user.id,
        category=payload.category,
        name=payload.name,
        district=payload.district,
        upazila=payload.upazila,
        address=payload.address,
        latitude=payload.latitude,
        longitude=payload.longitude,
        price_range_min=payload.price_range_min,
        price_range_max=payload.price_range_max,
        amenities=payload.amenities,
        tips=payload.tips,
        photo_urls=payload.photo_urls,
        embedded_video_urls=payload.embedded_video_urls,
        tags=payload.tags,
        status="pending_review",
    )
    session.add(contribution)
    upsert_location_from_contribution(session, contribution)
    maybe_create_accommodation_from_contribution(session, contribution)
    session.commit()
    session.refresh(contribution)
    return success_response(
        "Contribution created successfully", serialize_contribution_detail(contribution)
    )


@app.get(f"{API_PREFIX}/community/contributions")
def list_community_contributions(
    category: str | None = None,
    district: str | None = None,
    tag: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
):
    items = session.exec(select(CommunityContribution)).all()
    if category:
        items = [
            item for item in items if normalize(item.category) == normalize(category)
        ]
    if district:
        items = [
            item for item in items if normalize(item.district) == normalize(district)
        ]
    if tag:
        items = [item for item in items if tag in item.tags]
    items.sort(key=lambda item: item.created_at, reverse=True)
    paged, meta = paginate(items, page, limit)
    return success_response(
        "Contributions fetched successfully",
        [serialize_contribution_list_item(item) for item in paged],
        meta,
    )


@app.get(f"{API_PREFIX}/community/contributions/{{contribution_id}}")
def get_community_contribution(
    contribution_id: str, session: Session = Depends(get_session)
):
    contribution = get_or_404(
        session, CommunityContribution, contribution_id, "Contribution"
    )
    return success_response(
        "Contribution fetched successfully", serialize_contribution_detail(contribution)
    )


@app.patch(f"{API_PREFIX}/community/contributions/{{contribution_id}}")
def update_community_contribution(
    contribution_id: str,
    payload: CommunityContributionUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    contribution = get_or_404(
        session, CommunityContribution, contribution_id, "Contribution"
    )
    ensure_owner(current_user.id, contribution.user_id, "contribution")

    updates = payload.model_dump(exclude_unset=True)
    if "tags" in updates and updates["tags"] is not None:
        ensure_tags(updates["tags"])
    if (
        "category" in updates
        and updates["category"] is not None
        and updates["category"] not in COMMUNITY_CATEGORIES
    ):
        api_error(
            422,
            "Validation failed",
            {
                "category": [
                    f"Must be one of: {', '.join(sorted(COMMUNITY_CATEGORIES))}"
                ]
            },
        )

    next_min = updates.get("price_range_min", contribution.price_range_min)
    next_max = updates.get("price_range_max", contribution.price_range_max)
    ensure_price_range(next_min, next_max)

    for key, value in updates.items():
        setattr(contribution, key, value)
    touch(contribution)
    session.add(contribution)
    session.commit()
    session.refresh(contribution)
    return success_response(
        "Contribution updated successfully", serialize_contribution_detail(contribution)
    )


@app.delete(f"{API_PREFIX}/community/contributions/{{contribution_id}}")
def delete_community_contribution(
    contribution_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    contribution = get_or_404(
        session, CommunityContribution, contribution_id, "Contribution"
    )
    ensure_owner(current_user.id, contribution.user_id, "contribution")
    session.delete(contribution)
    session.commit()
    return success_response("Contribution deleted successfully", None)


# =============================================================================
# Feature 2: Group Trip Creation Page
# =============================================================================


@app.post(f"{API_PREFIX}/group-trips", status_code=status.HTTP_201_CREATED)
def create_group_trip(
    payload: GroupTripCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    ensure_visibility(payload.visibility)
    ensure_date_range(payload.start_date, payload.end_date)

    trip = GroupTrip(
        id=generate_id("group"),
        trip_name=payload.trip_name,
        destination=payload.destination,
        start_date=payload.start_date,
        end_date=payload.end_date,
        visibility=payload.visibility,
        description=payload.description,
        created_by=current_user.id,
        invite_code=build_invite_code(payload.destination),
        cover_image_url=payload.cover_image_url,
    )
    session.add(trip)
    session.add(
        GroupTripMember(
            id=generate_id("member"),
            group_trip_id=trip.id,
            user_id=current_user.id,
            role="Organizer",
        )
    )
    add_group_feed(
        session,
        trip.id,
        "trip_created",
        f"{current_user.name} created group trip {trip.trip_name}",
        current_user.id,
    )
    session.commit()
    session.refresh(trip)
    return success_response(
        "Group trip created successfully", serialize_group_trip(session, trip)
    )


@app.get(f"{API_PREFIX}/group-trips/my")
def get_my_group_trips(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    memberships = session.exec(
        select(GroupTripMember).where(GroupTripMember.user_id == current_user.id)
    ).all()
    member_trip_ids = {member.group_trip_id for member in memberships}
    trips = [
        trip
        for trip in session.exec(select(GroupTrip)).all()
        if trip.created_by == current_user.id or trip.id in member_trip_ids
    ]
    trips.sort(key=lambda item: item.created_at, reverse=True)
    paged, meta = paginate(trips, page, limit)
    return success_response(
        "Group trips fetched successfully",
        [serialize_group_trip(session, trip) for trip in paged],
        meta,
    )


@app.post(f"{API_PREFIX}/group-trips/join")
def join_group_trip(
    payload: GroupJoinRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    trips = session.exec(select(GroupTrip)).all()
    trip = next(
        (item for item in trips if item.invite_code == payload.invite_code), None
    )
    if not trip:
        api_error(404, "Group trip not found")
    assert trip is not None

    if get_group_member(session, trip.id, current_user.id):
        return success_response(
            "Already joined this group trip", serialize_group_trip(session, trip)
        )

    session.add(
        GroupTripMember(
            id=generate_id("member"),
            group_trip_id=trip.id,
            user_id=current_user.id,
            role="Member",
        )
    )
    add_group_feed(
        session,
        trip.id,
        "member_joined",
        f"{current_user.name} joined the trip",
        current_user.id,
    )
    create_notification(
        session,
        trip.created_by,
        "invite_join",
        "New group member",
        f"{current_user.name} joined your trip {trip.trip_name}.",
        {"group_trip_id": trip.id},
    )
    session.commit()
    return success_response(
        "Joined group trip successfully", serialize_group_trip(session, trip)
    )


@app.get(f"{API_PREFIX}/group-trips/overlapping-travelers")
def overlapping_travelers(
    destination: str,
    start_date: date,
    end_date: date,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    ensure_date_range(start_date, end_date)
    current_interests = set(current_user.interests)

    matching_trips = [
        trip
        for trip in session.exec(select(GroupTrip)).all()
        if normalize(trip.destination) == normalize(destination)
        and trip.visibility == "public"
        and trip.start_date <= end_date
        and trip.end_date >= start_date
    ]

    seen_users: set[str] = set()
    results: list[dict[str, Any]] = []
    for trip in matching_trips:
        members = session.exec(
            select(GroupTripMember).where(GroupTripMember.group_trip_id == trip.id)
        ).all()
        for member in members:
            if member.user_id == current_user.id or member.user_id in seen_users:
                continue
            user = session.get(User, member.user_id)
            if not user:
                continue
            seen_users.add(member.user_id)
            results.append(
                {
                    "user_id": user.id,
                    "name": user.name,
                    "avatar_url": user.avatar_url,
                    "travel_dates": {
                        "start_date": trip.start_date.isoformat(),
                        "end_date": trip.end_date.isoformat(),
                    },
                    "mutual_interests": sorted(
                        current_interests.intersection(set(user.interests))
                    ),
                }
            )

    return success_response("Overlapping travelers fetched successfully", results)


@app.get(f"{API_PREFIX}/group-trips/{{group_trip_id}}")
def get_group_trip(
    group_trip_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    trip = get_or_404(session, GroupTrip, group_trip_id, "Group trip")
    ensure_group_read_access(session, trip, current_user.id)
    return success_response(
        "Group trip fetched successfully",
        serialize_group_trip(session, trip, include_members=True),
    )


@app.patch(f"{API_PREFIX}/group-trips/{{group_trip_id}}")
def update_group_trip(
    group_trip_id: str,
    payload: GroupTripUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    trip = get_or_404(session, GroupTrip, group_trip_id, "Group trip")
    ensure_owner(current_user.id, trip.created_by, "group trip")
    updates = payload.model_dump(exclude_unset=True)

    next_start = updates.get("start_date", trip.start_date)
    next_end = updates.get("end_date", trip.end_date)
    ensure_date_range(next_start, next_end)
    if "visibility" in updates and updates["visibility"] is not None:
        ensure_visibility(updates["visibility"])

    for key, value in updates.items():
        setattr(trip, key, value)
    touch(trip)
    session.add(trip)
    add_group_feed(
        session,
        trip.id,
        "trip_updated",
        f"{current_user.name} updated {trip.trip_name}",
        current_user.id,
    )
    session.commit()
    session.refresh(trip)
    return success_response(
        "Group trip updated successfully",
        serialize_group_trip(session, trip, include_members=True),
    )


@app.delete(f"{API_PREFIX}/group-trips/{{group_trip_id}}")
def delete_group_trip(
    group_trip_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    trip = get_or_404(session, GroupTrip, group_trip_id, "Group trip")
    ensure_owner(current_user.id, trip.created_by, "group trip")

    polls = [
        item
        for item in session.exec(select(GroupPoll)).all()
        if item.group_trip_id == group_trip_id
    ]
    poll_ids = {item.id for item in polls}

    for item in session.exec(select(GroupTripMember)).all():
        if item.group_trip_id == group_trip_id:
            session.delete(item)
    for item in session.exec(select(GroupItineraryActivity)).all():
        if item.group_trip_id == group_trip_id:
            session.delete(item)
    for item in session.exec(select(GroupPresence)).all():
        if item.group_trip_id == group_trip_id:
            session.delete(item)
    for item in session.exec(select(GroupActivityFeed)).all():
        if item.group_trip_id == group_trip_id:
            session.delete(item)
    for item in polls:
        session.delete(item)
    for item in session.exec(select(GroupPollOption)).all():
        if item.poll_id in poll_ids:
            session.delete(item)
    for item in session.exec(select(GroupPollVote)).all():
        if item.poll_id in poll_ids:
            session.delete(item)

    session.delete(trip)
    session.commit()
    return success_response("Group trip deleted successfully", None)


@app.post(f"{API_PREFIX}/group-trips/{{group_trip_id}}/invite-link")
def generate_invite_link(
    group_trip_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    trip = get_or_404(session, GroupTrip, group_trip_id, "Group trip")
    ensure_owner(current_user.id, trip.created_by, "group trip")
    trip.invite_code = build_invite_code(trip.destination)
    touch(trip)
    session.add(trip)
    session.commit()
    session.refresh(trip)
    return success_response(
        "Invite link generated successfully",
        {
            "invite_code": trip.invite_code,
            "invite_link": build_invite_link(trip.invite_code),
        },
    )


# =============================================================================
# Member-2 APIs
# =============================================================================
# Feature 3: AI Itinerary Generation Page
# =============================================================================


@app.post(f"{API_PREFIX}/itineraries/generate", status_code=status.HTTP_201_CREATED)
def generate_itinerary(
    payload: ItineraryGenerateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if payload.duration_days < 1:
        api_error(
            422, "Validation failed", {"duration_days": ["Must be greater than 0"]}
        )
    if payload.budget <= 0:
        api_error(422, "Validation failed", {"budget": ["Must be greater than 0"]})

    days = generate_itinerary_days(session, payload)
    estimated_total_cost = calculate_itinerary_total(days)

    generated = GeneratedItinerary(
        id=generate_id("iti"),
        created_by=current_user.id,
        destination=payload.destination,
        duration_days=payload.duration_days,
        budget=payload.budget,
        travel_styles=payload.travel_styles,
        interests=payload.interests,
        group_type=payload.group_type,
        prioritize_hidden_gems=payload.prioritize_hidden_gems,
        estimated_total_cost=estimated_total_cost,
        days=days,
        request_context=payload.model_dump(),
    )
    session.add(generated)
    session.commit()
    session.refresh(generated)

    return success_response(
        "Itinerary generated successfully",
        {
            "itinerary_id": generated.id,
            "destination": generated.destination,
            "duration_days": generated.duration_days,
            "estimated_total_cost": generated.estimated_total_cost,
            "days": generated.days,
            "generated_at": isoformat(generated.created_at),
        },
    )


@app.post(f"{API_PREFIX}/itineraries", status_code=status.HTTP_201_CREATED)
def save_generated_itinerary(
    payload: SaveItineraryRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    generated = get_or_404(
        session,
        GeneratedItinerary,
        payload.generated_itinerary_id,
        "Generated itinerary",
    )
    ensure_owner(current_user.id, generated.created_by, "generated itinerary")

    saved = SavedItinerary(
        id=generate_id("saved"),
        generated_itinerary_id=generated.id,
        created_by=current_user.id,
        trip_name=payload.trip_name,
        destination=generated.destination,
        duration_days=generated.duration_days,
        budget_cap=generated.budget,
        notes=None,
        estimated_total_cost=generated.estimated_total_cost,
        days=generated.days,
    )
    session.add(saved)
    session.commit()
    session.refresh(saved)
    return success_response(
        "Itinerary saved successfully", serialize_saved_itinerary(saved)
    )


@app.get(f"{API_PREFIX}/itineraries/{{itinerary_id}}")
def get_saved_itinerary(
    itinerary_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    itinerary = get_or_404(session, SavedItinerary, itinerary_id, "Itinerary")
    ensure_owner(current_user.id, itinerary.created_by, "itinerary")
    return success_response(
        "Itinerary fetched successfully", serialize_saved_itinerary(itinerary)
    )


@app.patch(f"{API_PREFIX}/itineraries/{{itinerary_id}}")
def update_saved_itinerary(
    itinerary_id: str,
    payload: SavedItineraryUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    itinerary = get_or_404(session, SavedItinerary, itinerary_id, "Itinerary")
    ensure_owner(current_user.id, itinerary.created_by, "itinerary")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(itinerary, key, value)

    if payload.days is not None:
        itinerary.duration_days = len(payload.days)
        itinerary.estimated_total_cost = calculate_itinerary_total(payload.days)

    touch(itinerary)
    session.add(itinerary)
    session.commit()
    session.refresh(itinerary)
    return success_response(
        "Itinerary updated successfully", serialize_saved_itinerary(itinerary)
    )


@app.delete(f"{API_PREFIX}/itineraries/{{itinerary_id}}")
def delete_saved_itinerary(
    itinerary_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    itinerary = get_or_404(session, SavedItinerary, itinerary_id, "Itinerary")
    ensure_owner(current_user.id, itinerary.created_by, "itinerary")

    for chat in session.exec(select(ItineraryChatMessage)).all():
        if chat.itinerary_id == itinerary_id:
            session.delete(chat)
    session.delete(itinerary)
    session.commit()
    return success_response("Itinerary deleted successfully", None)


# =============================================================================
# Feature 4: Accommodation Recommendations Page
# =============================================================================


@app.get(f"{API_PREFIX}/accommodations/recommendations")
def get_accommodation_recommendations(
    destination: str,
    type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    amenities: str | None = None,
    min_rating: float | None = None,
    sort_by: str = "rating",
    session: Session = Depends(get_session),
):
    types = {normalize(item) for item in parse_csv_param(type)}
    required_amenities = {normalize(item) for item in parse_csv_param(amenities)}

    items = [
        item
        for item in session.exec(select(Accommodation)).all()
        if text_match(destination, item.destination, item.name)
    ]
    if types:
        items = [item for item in items if normalize(item.type) in types]
    if min_price is not None:
        items = [item for item in items if item.price_per_night >= min_price]
    if max_price is not None:
        items = [item for item in items if item.price_per_night <= max_price]
    if min_rating is not None:
        items = [item for item in items if item.star_rating >= min_rating]
    if required_amenities:
        items = [
            item
            for item in items
            if required_amenities.issubset(
                {normalize(amenity) for amenity in item.amenities}
            )
        ]

    if sort_by == "distance":
        items.sort(key=lambda item: item.distance_to_nearest_attraction_km)
    elif sort_by == "price":
        items.sort(key=lambda item: item.price_per_night)
    else:
        items.sort(
            key=lambda item: (item.star_rating, -item.price_per_night), reverse=True
        )

    return success_response(
        "Accommodation recommendations fetched successfully",
        {
            "items": [serialize_accommodation(item) for item in items],
            "map_pins": [
                {
                    "id": item.id,
                    "type": "accommodation",
                    "latitude": item.latitude,
                    "longitude": item.longitude,
                }
                for item in items
            ],
        },
    )


@app.post(f"{API_PREFIX}/accommodations/ai-top-pick")
def get_accommodation_ai_top_pick(
    payload: AccommodationTopPickRequest,
    session: Session = Depends(get_session),
):
    accommodations = [
        item
        for item in session.exec(select(Accommodation)).all()
        if text_match(payload.destination, item.destination, item.name)
    ]
    if not accommodations:
        api_error(404, "No accommodations found for this destination")

    desired_amenities = {normalize(item) for item in payload.preferred_amenities}
    scored: list[tuple[float, Accommodation]] = []
    for item in accommodations:
        item_amenities = {normalize(amenity) for amenity in item.amenities}
        amenity_score = len(desired_amenities.intersection(item_amenities)) * 2
        budget_score = (
            2
            if item.price_per_night <= payload.budget_per_night
            else max(0, 2 - ((item.price_per_night - payload.budget_per_night) / 1000))
        )
        attraction_score = max(0, 3 - item.distance_to_nearest_attraction_km)
        total_score = amenity_score + budget_score + attraction_score + item.star_rating
        scored.append((total_score, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    best = scored[0][1]
    return success_response(
        "AI top pick generated successfully",
        {
            "accommodation_id": best.id,
            "name": best.name,
            "price_per_night": best.price_per_night,
            "reason": "Best value based on proximity to planned attractions, price, and amenity match.",
            "comparison_badges": [
                "Strong amenity match",
                "Good travel-time balance",
            ],
        },
    )


@app.get(f"{API_PREFIX}/accommodations/{{accommodation_id}}")
def get_accommodation_detail(
    accommodation_id: str, session: Session = Depends(get_session)
):
    accommodation = get_or_404(
        session, Accommodation, accommodation_id, "Accommodation"
    )
    return success_response(
        "Accommodation fetched successfully",
        serialize_accommodation(accommodation, detailed=True),
    )


# =============================================================================
# Member-3 APIs
# =============================================================================
# Feature 5: Nomad Metrics & Interactive Map Page
# =============================================================================


@app.get(f"{API_PREFIX}/locations/{{location_id}}/nomad-metrics")
def get_nomad_metrics(location_id: str, session: Session = Depends(get_session)):
    location = get_or_404(session, Location, location_id, "Location")
    ratings = [
        item
        for item in session.exec(select(NomadMetricRating)).all()
        if item.location_id == location_id
    ]
    return success_response(
        "Nomad metrics fetched successfully", build_nomad_metrics(location, ratings)
    )


@app.get(f"{API_PREFIX}/locations/{{location_id}}/nomad-map")
def get_nomad_map(
    location_id: str, layer: str, session: Session = Depends(get_session)
):
    location = get_or_404(session, Location, location_id, "Location")
    return success_response(
        "Map layer fetched successfully", build_nomad_map(session, location, layer)
    )


@app.get(f"{API_PREFIX}/locations/{{location_id}}/nomad-metrics/ratings")
def list_nomad_metric_ratings(
    location_id: str, session: Session = Depends(get_session)
):
    _ = get_or_404(session, Location, location_id, "Location")
    ratings = [
        item
        for item in session.exec(select(NomadMetricRating)).all()
        if item.location_id == location_id
    ]
    ratings.sort(key=lambda item: item.created_at, reverse=True)
    return success_response(
        "Nomad metric ratings fetched successfully",
        [serialize_nomad_rating(session, item) for item in ratings],
    )


@app.post(
    f"{API_PREFIX}/locations/{{location_id}}/nomad-metrics/ratings",
    status_code=status.HTTP_201_CREATED,
)
def create_nomad_metric_rating(
    location_id: str,
    payload: NomadMetricsRatingCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    _ = get_or_404(session, Location, location_id, "Location")
    existing = [
        item
        for item in session.exec(select(NomadMetricRating)).all()
        if item.location_id == location_id and item.user_id == current_user.id
    ]
    if existing:
        api_error(409, "You already submitted a rating for this location")

    rating = NomadMetricRating(
        id=generate_id("rating"),
        location_id=location_id,
        user_id=current_user.id,
        carrier_reports=payload.carrier_reports,
        solo_female_safety_score=payload.solo_female_safety_score,
        solo_female_safety_tip=payload.solo_female_safety_tip,
        digital_payment_reports=payload.digital_payment_reports,
        general_infrastructure=payload.general_infrastructure,
    )
    session.add(rating)
    session.commit()
    session.refresh(rating)
    return success_response(
        "Nomad metrics rating created successfully",
        serialize_nomad_rating(session, rating),
    )


@app.patch(
    f"{API_PREFIX}/locations/{{location_id}}/nomad-metrics/ratings/{{rating_id}}"
)
def update_nomad_metric_rating(
    location_id: str,
    rating_id: str,
    payload: NomadMetricsRatingUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    _ = get_or_404(session, Location, location_id, "Location")
    rating = get_or_404(session, NomadMetricRating, rating_id, "Nomad metrics rating")
    if rating.location_id != location_id:
        api_error(404, "Nomad metrics rating not found")
    ensure_owner(current_user.id, rating.user_id, "nomad metrics rating")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(rating, key, value)
    touch(rating)
    session.add(rating)
    session.commit()
    session.refresh(rating)
    return success_response(
        "Nomad metrics rating updated successfully",
        serialize_nomad_rating(session, rating),
    )


@app.delete(
    f"{API_PREFIX}/locations/{{location_id}}/nomad-metrics/ratings/{{rating_id}}"
)
def delete_nomad_metric_rating(
    location_id: str,
    rating_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    _ = get_or_404(session, Location, location_id, "Location")
    rating = get_or_404(session, NomadMetricRating, rating_id, "Nomad metrics rating")
    if rating.location_id != location_id:
        api_error(404, "Nomad metrics rating not found")
    ensure_owner(current_user.id, rating.user_id, "nomad metrics rating")
    session.delete(rating)
    session.commit()
    return success_response("Nomad metrics rating deleted successfully", None)


# =============================================================================
# Feature 6: Live Budget Tracker Page
# =============================================================================


@app.post(f"{API_PREFIX}/trips/{{trip_id}}/budget", status_code=status.HTTP_201_CREATED)
def create_budget(
    trip_id: str,
    payload: BudgetCreateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    existing = next(
        (
            item
            for item in session.exec(select(TripBudget)).all()
            if item.trip_id == trip_id
        ),
        None,
    )
    if existing:
        api_error(409, "Budget already exists for this trip")
    if payload.total_budget <= 0:
        api_error(
            422, "Validation failed", {"total_budget": ["Must be greater than 0"]}
        )

    budget = TripBudget(
        id=generate_id("budget"),
        trip_id=trip_id,
        created_by=current_user.id,
        total_budget=payload.total_budget,
        category_allocations=payload.category_allocations,
    )
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return success_response(
        "Budget tracker created successfully",
        {
            "trip_id": budget.trip_id,
            "total_budget": budget.total_budget,
            "category_allocations": budget.category_allocations,
            "created_at": isoformat(budget.created_at),
        },
    )


@app.get(f"{API_PREFIX}/trips/{{trip_id}}/budget")
def get_budget_summary(
    trip_id: str,
    session: Session = Depends(get_session),
):
    return success_response(
        "Budget summary fetched successfully", compute_budget_summary(session, trip_id)
    )


@app.post(
    f"{API_PREFIX}/trips/{{trip_id}}/budget/expenses",
    status_code=status.HTTP_201_CREATED,
)
def add_expense(
    trip_id: str,
    payload: ExpenseCreateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    budget = next(
        (
            item
            for item in session.exec(select(TripBudget)).all()
            if item.trip_id == trip_id
        ),
        None,
    )
    if not budget:
        api_error(404, "Budget not found")
    assert budget is not None

    expense = TripExpense(
        id=generate_id("exp"),
        trip_id=trip_id,
        created_by=current_user.id,
        amount=payload.amount,
        category=payload.category,
        description=payload.description,
        expense_date=payload.expense_date,
        receipt_photo_url=payload.receipt_photo_url,
    )
    session.add(expense)
    session.commit()
    session.refresh(expense)

    summary = compute_budget_summary(session, trip_id)
    maybe_emit_budget_notifications(session, budget, summary)
    session.commit()

    return success_response("Expense added successfully", serialize_expense(expense))


@app.get(f"{API_PREFIX}/trips/{{trip_id}}/budget/expenses")
def get_expense_log(
    trip_id: str,
    group_by: str | None = Query(None),
    session: Session = Depends(get_session),
):
    expenses = [
        item
        for item in session.exec(select(TripExpense)).all()
        if item.trip_id == trip_id
    ]
    expenses.sort(key=lambda item: (item.expense_date, item.created_at), reverse=True)

    if group_by == "day":
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        totals: dict[str, float] = defaultdict(float)
        for item in expenses:
            day_key = item.expense_date.isoformat()
            grouped[day_key].append(serialize_expense(item))
            totals[day_key] += item.amount
        data = [
            {"date": day, "expenses": grouped[day], "total": round(totals[day], 2)}
            for day in sorted(grouped.keys(), reverse=True)
        ]
    else:
        data = [serialize_expense(item) for item in expenses]

    return success_response("Expense log fetched successfully", data)


@app.patch(f"{API_PREFIX}/trips/{{trip_id}}/budget/expenses/{{expense_id}}")
def update_expense(
    trip_id: str,
    expense_id: str,
    payload: ExpenseUpdateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    expense = get_or_404(session, TripExpense, expense_id, "Expense")
    if expense.trip_id != trip_id:
        api_error(404, "Expense not found")
    ensure_owner(current_user.id, expense.created_by, "expense")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(expense, key, value)
    touch(expense)
    session.add(expense)
    session.commit()
    session.refresh(expense)

    budget = next(
        (
            item
            for item in session.exec(select(TripBudget)).all()
            if item.trip_id == trip_id
        ),
        None,
    )
    if budget:
        summary = compute_budget_summary(session, trip_id)
        maybe_emit_budget_notifications(session, budget, summary)
        session.commit()

    return success_response("Expense updated successfully", serialize_expense(expense))


@app.delete(f"{API_PREFIX}/trips/{{trip_id}}/budget/expenses/{{expense_id}}")
def delete_expense(
    trip_id: str,
    expense_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    expense = get_or_404(session, TripExpense, expense_id, "Expense")
    if expense.trip_id != trip_id:
        api_error(404, "Expense not found")
    ensure_owner(current_user.id, expense.created_by, "expense")
    session.delete(expense)
    session.commit()
    return success_response("Expense deleted successfully", None)


@app.get(f"{API_PREFIX}/trips/{{trip_id}}/budget/analytics")
def get_budget_analytics(trip_id: str, session: Session = Depends(get_session)):
    summary = compute_budget_summary(session, trip_id)
    budget = next(
        (
            item
            for item in session.exec(select(TripBudget)).all()
            if item.trip_id == trip_id
        ),
        None,
    )
    expenses = [
        item
        for item in session.exec(select(TripExpense)).all()
        if item.trip_id == trip_id
    ]

    daily_trend_map: dict[str, float] = defaultdict(float)
    for expense in expenses:
        daily_trend_map[expense.expense_date.isoformat()] += expense.amount

    analytics = {
        "pie_chart": [
            {"category": key, "amount": value}
            for key, value in summary["category_breakdown"].items()
        ],
        "allocation_vs_actual": [
            {
                "category": category,
                "allocated": amount,
                "actual": round(summary["category_breakdown"].get(category, 0), 2),
            }
            for category, amount in (
                budget.category_allocations.items() if budget else []
            )
        ],
        "daily_trend": [
            {"date": key, "amount": round(value, 2)}
            for key, value in sorted(daily_trend_map.items())
        ],
    }
    return success_response("Budget analytics fetched successfully", analytics)


# =============================================================================
# Member-4 APIs
# =============================================================================
# Feature 7: AI Chatbot for Itinerary Refinement Page
# =============================================================================


@app.post(f"{API_PREFIX}/itineraries/{{itinerary_id}}/chat")
def send_itinerary_chat_message(
    itinerary_id: str,
    payload: ItineraryChatRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    itinerary = get_or_404(session, SavedItinerary, itinerary_id, "Itinerary")
    ensure_owner(current_user.id, itinerary.created_by, "itinerary")

    chat_result = build_chat_refinement(itinerary, payload.message)
    chat_message = ItineraryChatMessage(
        id=generate_id("chat"),
        itinerary_id=itinerary_id,
        user_id=current_user.id,
        user_message=payload.message,
        assistant_reply=chat_result["reply"],
        context_version=payload.context_version,
        suggested_changes=chat_result["suggested_changes"],
        updated_cost_summary=chat_result["updated_cost_summary"],
        updated_itinerary_preview=chat_result["updated_itinerary_preview"],
    )
    session.add(chat_message)
    session.commit()
    session.refresh(chat_message)

    return success_response(
        "AI response generated successfully",
        {
            "reply": chat_message.assistant_reply,
            "suggested_changes": chat_message.suggested_changes,
            "updated_cost_summary": chat_message.updated_cost_summary,
            "updated_itinerary_preview": chat_message.updated_itinerary_preview,
        },
    )


@app.post(f"{API_PREFIX}/itineraries/{{itinerary_id}}/chat/apply")
def apply_itinerary_chat_changes(
    itinerary_id: str,
    payload: ItineraryChatApplyRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    itinerary = get_or_404(session, SavedItinerary, itinerary_id, "Itinerary")
    ensure_owner(current_user.id, itinerary.created_by, "itinerary")

    history = [
        item
        for item in session.exec(select(ItineraryChatMessage)).all()
        if item.itinerary_id == itinerary_id
    ]
    history.sort(key=lambda item: item.created_at, reverse=True)
    if not history:
        api_error(404, "No chat history found for this itinerary")
    if not payload.accepted_change_ids:
        api_error(
            422,
            "Validation failed",
            {"accepted_change_ids": ["At least one change id is required"]},
        )

    latest = history[0]
    accepted_set = set(payload.accepted_change_ids)
    valid_ids = {change.get("id") for change in latest.suggested_changes}
    if not accepted_set.intersection(valid_ids):
        api_error(
            422,
            "Validation failed",
            {
                "accepted_change_ids": [
                    "No matching change ids found in latest chat response"
                ]
            },
        )

    updated_days = deepcopy(itinerary.days)
    preview_by_day = {
        item["day"]: item["activities"]
        for item in latest.updated_itinerary_preview
        if "day" in item
    }

    for day in updated_days:
        if day.get("day") in preview_by_day:
            day["activities"] = preview_by_day[day["day"]]

    itinerary.days = updated_days
    itinerary.estimated_total_cost = float(
        latest.updated_cost_summary.get("new_total", itinerary.estimated_total_cost)
    )
    latest.applied_change_ids = sorted(accepted_set)
    touch(itinerary)
    touch(latest)

    session.add(itinerary)
    session.add(latest)
    session.commit()
    session.refresh(itinerary)

    return success_response(
        "AI refinement changes applied successfully",
        serialize_saved_itinerary(itinerary),
    )


@app.get(f"{API_PREFIX}/itineraries/{{itinerary_id}}/chat/history")
def get_itinerary_chat_history(
    itinerary_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    itinerary = get_or_404(session, SavedItinerary, itinerary_id, "Itinerary")
    ensure_owner(current_user.id, itinerary.created_by, "itinerary")
    history = [
        item
        for item in session.exec(select(ItineraryChatMessage)).all()
        if item.itinerary_id == itinerary_id
    ]
    history.sort(key=lambda item: item.created_at)
    return success_response(
        "Chat history fetched successfully",
        [
            {
                "id": item.id,
                "message": item.user_message,
                "reply": item.assistant_reply,
                "context_version": item.context_version,
                "suggested_changes": item.suggested_changes,
                "updated_cost_summary": item.updated_cost_summary,
                "updated_itinerary_preview": item.updated_itinerary_preview,
                "applied_change_ids": item.applied_change_ids,
                "created_at": isoformat(item.created_at),
            }
            for item in history
        ],
    )


@app.get(f"{API_PREFIX}/seasonal-alerts")
def get_seasonal_alert(destination: str, travel_month: str):
    rainy_months = {"june", "july", "august", "september"}
    cool_months = ["October", "November", "December", "January", "February"]

    month_normalized = travel_month.strip().lower()
    if month_normalized in rainy_months:
        data = {
            "destination": destination,
            "travel_month": travel_month,
            "alert_level": "warning",
            "title": f"Seasonal caution for {destination}",
            "summary": f"Heavy rainfall is likely around {destination} during {travel_month}. Some routes may be slower or waterlogged.",
            "recommended_months": cool_months,
            "tips": [
                "Carry waterproof bags for electronics.",
                "Keep backup transport options.",
                "Check local road and weather conditions before departure.",
            ],
        }
    else:
        data = {
            "destination": destination,
            "travel_month": travel_month,
            "alert_level": "info",
            "title": f"Good travel window for {destination}",
            "summary": f"{travel_month} is generally a more stable month to travel in {destination}.",
            "recommended_months": cool_months,
            "tips": [
                "Book popular stays early in peak season.",
                "Carry cash for remote stops.",
                "Keep a light rain layer regardless of season.",
            ],
        }
    return success_response("Seasonal alert fetched successfully", data)


# =============================================================================
# Feature 8: Collaborative Group Planning & Polling Page
# =============================================================================


@app.get(f"{API_PREFIX}/group-trips/{{group_trip_id}}/itinerary")
def get_group_itinerary(
    group_trip_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    trip = get_or_404(session, GroupTrip, group_trip_id, "Group trip")
    ensure_group_read_access(session, trip, current_user.id)
    return success_response(
        "Group itinerary fetched successfully",
        build_group_itinerary(session, group_trip_id),
    )


@app.post(
    f"{API_PREFIX}/group-trips/{{group_trip_id}}/itinerary/activities",
    status_code=status.HTTP_201_CREATED,
)
def add_group_itinerary_activity(
    group_trip_id: str,
    payload: GroupActivityCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    trip = get_or_404(session, GroupTrip, group_trip_id, "Group trip")
    ensure_group_member(session, trip.id, current_user.id)

    activity = GroupItineraryActivity(
        id=generate_id("act"),
        group_trip_id=group_trip_id,
        day=payload.day,
        title=payload.title,
        time=payload.time,
        location_id=payload.location_id,
        added_by=current_user.id,
        status="under_vote",
        vote_count=0,
    )
    session.add(activity)
    add_group_feed(
        session,
        group_trip_id,
        "activity_added",
        f"{current_user.name} added {payload.title} to Day {payload.day}",
        current_user.id,
    )
    session.commit()
    session.refresh(activity)
    return success_response(
        "Activity added successfully", serialize_group_activity(session, activity)
    )


@app.patch(
    f"{API_PREFIX}/group-trips/{{group_trip_id}}/itinerary/activities/{{activity_id}}"
)
def update_group_itinerary_activity(
    group_trip_id: str,
    activity_id: str,
    payload: GroupActivityUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    trip = get_or_404(session, GroupTrip, group_trip_id, "Group trip")
    ensure_group_member(session, trip.id, current_user.id)

    activity = get_or_404(session, GroupItineraryActivity, activity_id, "Activity")
    if activity.group_trip_id != group_trip_id:
        api_error(404, "Activity not found")
    if activity.added_by != current_user.id and trip.created_by != current_user.id:
        api_error(403, "You do not have permission to modify this activity")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(activity, key, value)
    touch(activity)
    session.add(activity)
    add_group_feed(
        session,
        group_trip_id,
        "activity_updated",
        f"{current_user.name} updated activity {activity.title}",
        current_user.id,
    )
    session.commit()
    session.refresh(activity)
    return success_response(
        "Activity updated successfully", serialize_group_activity(session, activity)
    )


@app.delete(
    f"{API_PREFIX}/group-trips/{{group_trip_id}}/itinerary/activities/{{activity_id}}"
)
def delete_group_itinerary_activity(
    group_trip_id: str,
    activity_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    trip = get_or_404(session, GroupTrip, group_trip_id, "Group trip")
    ensure_group_member(session, trip.id, current_user.id)

    activity = get_or_404(session, GroupItineraryActivity, activity_id, "Activity")
    if activity.group_trip_id != group_trip_id:
        api_error(404, "Activity not found")
    if activity.added_by != current_user.id and trip.created_by != current_user.id:
        api_error(403, "You do not have permission to delete this activity")

    add_group_feed(
        session,
        group_trip_id,
        "activity_deleted",
        f"{current_user.name} removed {activity.title}",
        current_user.id,
    )
    session.delete(activity)
    session.commit()
    return success_response("Activity deleted successfully", None)


@app.post(f"{API_PREFIX}/group-trips/{{group_trip_id}}/presence")
def upsert_group_presence(
    group_trip_id: str,
    payload: GroupPresenceUpsert,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    trip = get_or_404(session, GroupTrip, group_trip_id, "Group trip")
    member = ensure_group_member(session, trip.id, current_user.id)

    existing = next(
        (
            item
            for item in session.exec(select(GroupPresence)).all()
            if item.group_trip_id == group_trip_id and item.user_id == current_user.id
        ),
        None,
    )
    if existing:
        existing.status = payload.status
        existing.role = payload.role or member.role
        existing.editing_target = payload.editing_target
        existing.presence_color = payload.presence_color or existing.presence_color
        touch(existing)
        session.add(existing)
        session.commit()
        session.refresh(existing)
        row = existing
    else:
        row = GroupPresence(
            id=generate_id("presence"),
            group_trip_id=group_trip_id,
            user_id=current_user.id,
            status=payload.status,
            role=payload.role or member.role,
            editing_target=payload.editing_target,
            presence_color=payload.presence_color
            or deterministic_color(current_user.id),
        )
        session.add(row)
        session.commit()
        session.refresh(row)

    return success_response(
        "Presence updated successfully",
        {
            "user_id": row.user_id,
            "name": get_user_summary(session, row.user_id)["name"],
            "status": row.status,
            "role": row.role,
            "editing_target": row.editing_target,
            "presence_color": row.presence_color,
        },
    )


@app.get(f"{API_PREFIX}/group-trips/{{group_trip_id}}/presence")
def get_group_presence(
    group_trip_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    trip = get_or_404(session, GroupTrip, group_trip_id, "Group trip")
    ensure_group_read_access(session, trip, current_user.id)

    members = session.exec(
        select(GroupTripMember).where(GroupTripMember.group_trip_id == group_trip_id)
    ).all()
    presence_rows = {
        item.user_id: item
        for item in session.exec(select(GroupPresence)).all()
        if item.group_trip_id == group_trip_id
    }

    result = []
    for member in members:
        row = presence_rows.get(member.user_id)
        profile = get_user_summary(session, member.user_id)
        result.append(
            {
                "user_id": member.user_id,
                "name": profile["name"],
                "status": row.status if row else "offline",
                "role": row.role if row else member.role,
                "editing_target": row.editing_target if row else None,
                "presence_color": row.presence_color
                if row
                else deterministic_color(member.user_id),
            }
        )

    return success_response("Presence data fetched successfully", result)


@app.post(
    f"{API_PREFIX}/group-trips/{{group_trip_id}}/polls",
    status_code=status.HTTP_201_CREATED,
)
def create_poll(
    group_trip_id: str,
    payload: PollCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    trip = get_or_404(session, GroupTrip, group_trip_id, "Group trip")
    ensure_group_member(session, trip.id, current_user.id)

    if len(payload.options) < 2:
        api_error(
            422,
            "Validation failed",
            {"options": ["At least two poll options are required"]},
        )

    poll = GroupPoll(
        id=generate_id("poll"),
        group_trip_id=group_trip_id,
        question=payload.question,
        type=payload.type,
        deadline=payload.deadline,
        status="active",
        created_by=current_user.id,
    )
    session.add(poll)

    for option in payload.options:
        session.add(
            GroupPollOption(
                id=generate_id("opt"),
                poll_id=poll.id,
                location_id=option.location_id,
                label=option.label,
            )
        )

    add_group_feed(
        session,
        group_trip_id,
        "poll_created",
        f"New poll: {payload.question}",
        current_user.id,
    )
    session.commit()
    session.refresh(poll)
    return success_response("Poll created successfully", serialize_poll(session, poll))


@app.post(f"{API_PREFIX}/group-trips/{{group_trip_id}}/polls/{{poll_id}}/vote")
def vote_on_poll(
    group_trip_id: str,
    poll_id: str,
    payload: PollVoteRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    trip = get_or_404(session, GroupTrip, group_trip_id, "Group trip")
    ensure_group_member(session, trip.id, current_user.id)
    poll = get_or_404(session, GroupPoll, poll_id, "Poll")
    if poll.group_trip_id != group_trip_id:
        api_error(404, "Poll not found")
    if not poll_is_active(poll):
        api_error(400, "Poll is closed")

    options = session.exec(
        select(GroupPollOption).where(GroupPollOption.poll_id == poll_id)
    ).all()
    option_ids = {option.id for option in options}
    if payload.option_id not in option_ids:
        api_error(422, "Validation failed", {"option_id": ["Invalid poll option"]})

    existing_vote = next(
        (
            vote
            for vote in session.exec(select(GroupPollVote)).all()
            if vote.poll_id == poll_id and vote.user_id == current_user.id
        ),
        None,
    )
    if existing_vote:
        existing_vote.option_id = payload.option_id
        touch(existing_vote)
        session.add(existing_vote)
    else:
        session.add(
            GroupPollVote(
                id=generate_id("vote"),
                poll_id=poll_id,
                option_id=payload.option_id,
                user_id=current_user.id,
            )
        )

    selected_option = next(
        option for option in options if option.id == payload.option_id
    )
    add_group_feed(
        session,
        group_trip_id,
        "vote_cast",
        f"{current_user.name} voted for {selected_option.label}",
        current_user.id,
    )
    session.commit()
    session.refresh(poll)
    return success_response("Vote cast successfully", serialize_poll(session, poll))


@app.get(f"{API_PREFIX}/group-trips/{{group_trip_id}}/polls")
def list_group_polls(
    group_trip_id: str,
    status_filter: str | None = Query(default=None, alias="status"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    trip = get_or_404(session, GroupTrip, group_trip_id, "Group trip")
    ensure_group_read_access(session, trip, current_user.id)

    polls = [
        item
        for item in session.exec(select(GroupPoll)).all()
        if item.group_trip_id == group_trip_id
    ]
    if status_filter and status_filter != "all":
        if status_filter == "active":
            polls = [item for item in polls if poll_is_active(item)]
        elif status_filter == "closed":
            polls = [item for item in polls if not poll_is_active(item)]
    polls.sort(key=lambda item: item.created_at, reverse=True)
    return success_response(
        "Polls fetched successfully", [serialize_poll(session, item) for item in polls]
    )


@app.get(f"{API_PREFIX}/group-trips/{{group_trip_id}}/activity-feed")
def get_group_activity_feed(
    group_trip_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    trip = get_or_404(session, GroupTrip, group_trip_id, "Group trip")
    ensure_group_read_access(session, trip, current_user.id)

    feeds = [
        item
        for item in session.exec(select(GroupActivityFeed)).all()
        if item.group_trip_id == group_trip_id
    ]
    feeds.sort(key=lambda item: item.created_at, reverse=True)
    return success_response(
        "Activity feed fetched successfully",
        [serialize_feed_item(item) for item in feeds],
    )


# =============================================================================
# Root
# =============================================================================


@app.get("/")
def root():
    return {
        "name": "Bangla Trek API",
        "version": "0.1.0",
        "base_url": API_PREFIX,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    # port = int(os.getenv("PORT", os.getenv("UVICORN_PORT", 8000)))
    uvicorn.run("main:app", host="0.0.0.0", port=1100, reload=True)
