#!/usr/bin/env python3
"""
Final all-in-one seed for Bangla Trek.

Run from backend/ after migrations:
    uv run python scripts/final_seed.py

The script is deterministic and rerunnable. It cleans rows created by this seed
in dependency order, keeps the seed users, and recreates demo data for the
migrated project tables.
"""

import os
import sys
import uuid
from datetime import date, datetime

from sqlalchemy import inspect, or_

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal, engine
from app.models.buddy_match import BuddyMatch
from app.models.community_entry import CommunityEntry
from app.models.emergency_facility import EmergencyFacility
from app.models.entry_photo import EntryPhoto
from app.models.entry_review import EntryReview
from app.models.entry_review_photo import EntryReviewPhoto
from app.models.entry_video_embed import EntryVideoEmbed
from app.models.group_activity import GroupActivity
from app.models.group_trip import GroupTrip, GroupTripMember
from app.models.itinerary import Itinerary, ItineraryActivity
from app.models.nomad_metrics import NomadMetric
from app.models.poll import Poll, PollOption, Vote
from app.models.transit_blueprint import TransitBlueprint, TransitBlueprintStep
from app.models.transit_fare_contribution import TransitFareContribution
from app.models.trip_budget import GroupTripBudget, GroupTripExpense
from app.models.user import User
from app.models.user_location import UserLocation


SEED_NAMESPACE = uuid.UUID("6f5c3a19-df87-4f2e-9c7c-0fce8b780001")


def seed_id(kind: str, key: str) -> uuid.UUID:
    return uuid.uuid5(SEED_NAMESPACE, f"{kind}:{key}")


def seed_ids(kind: str, keys: list[str]) -> list[uuid.UUID]:
    return [seed_id(kind, key) for key in keys]


USERS = [
    {
        "key": "demo",
        "google_id": "seed-google-demo",
        "email": "demo@banglatrek.com",
        "name": "Demo Traveler",
        "picture_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Demo",
    },
    {
        "key": "ayesha",
        "google_id": "seed-google-ayesha",
        "email": "ayesha@banglatrek.com",
        "name": "Ayesha Rahman",
        "picture_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Ayesha",
    },
    {
        "key": "rafi",
        "google_id": "seed-google-rafi",
        "email": "rafi@banglatrek.com",
        "name": "Rafi Chowdhury",
        "picture_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Rafi",
    },
    {
        "key": "nadia",
        "google_id": "seed-google-nadia",
        "email": "nadia@banglatrek.com",
        "name": "Nadia Karim",
        "picture_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Nadia",
    },
]


COMMUNITY_ENTRIES = [
    {
        "key": "ratargul",
        "author": "demo",
        "name": "Ratargul Swamp Forest",
        "category": "attraction",
        "location": "Sylhet",
        "latitude": 25.0075,
        "longitude": 91.9736,
        "price_range": "budget",
        "tags": ["trending", "hidden_gem"],
        "amenities": ["Boat Trip", "Wildlife", "Photography", "Local Guide"],
        "travel_tips": "Best during monsoon when the water level is high. Hire a boat from the local ghat and keep dry bags for phones.",
        "photos": [
            ("https://images.unsplash.com/photo-1590603740183-980e7f6920eb?q=80&w=1000", "Boat ride through the swamp"),
        ],
        "videos": [("https://www.youtube.com/watch?v=kYv_w2lM_w4", "youtube")],
    },
    {
        "key": "jaflong",
        "author": "rafi",
        "name": "Jaflong Riverside",
        "category": "attraction",
        "location": "Jaflong, Sylhet",
        "latitude": 25.1648,
        "longitude": 92.0177,
        "price_range": "budget",
        "tags": ["trending"],
        "amenities": ["River View", "Photography", "Local Food"],
        "travel_tips": "Go early for clearer views of the Meghalaya hills. The river stones get slippery after rain.",
        "photos": [
            ("https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1000", "River and hill view"),
        ],
        "videos": [],
    },
    {
        "key": "lawachara",
        "author": "ayesha",
        "name": "Lawachara National Park",
        "category": "attraction",
        "location": "Srimangal, Sylhet",
        "latitude": 24.3210,
        "longitude": 91.7900,
        "price_range": "budget",
        "tags": ["hidden_gem"],
        "amenities": ["Forest Trail", "Birdwatching", "Guide"],
        "travel_tips": "Visit around sunrise for the best wildlife sightings. A local guide helps a lot with spotting hoolock gibbons.",
        "photos": [
            ("https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=1000", "Forest trail"),
        ],
        "videos": [],
    },
    {
        "key": "sajek",
        "author": "demo",
        "name": "Sajek Valley",
        "category": "attraction",
        "location": "Baghaichhari, Rangamati",
        "latitude": 23.3814,
        "longitude": 92.2938,
        "price_range": "mid_range",
        "tags": ["trending", "hidden_gem"],
        "amenities": ["Cloud View", "Hiking", "Local Food", "Resorts"],
        "travel_tips": "Carry cash, warm layers, and a power bank. The army checkpoint timing matters, so leave Khagrachhari early.",
        "photos": [
            ("https://images.unsplash.com/photo-1658383898607-6b92e8196e33?q=80&w=1000", "Clouds over Sajek"),
            ("https://images.unsplash.com/photo-1658383895221-173f07c6a9d0?q=80&w=1000", "Hill cottage"),
        ],
        "videos": [("https://www.youtube.com/watch?v=07d2dXHYb94", "youtube")],
    },
    {
        "key": "laboni",
        "author": "ayesha",
        "name": "Laboni Beach",
        "category": "attraction",
        "location": "Cox's Bazar",
        "latitude": 21.4290,
        "longitude": 91.9748,
        "price_range": "budget",
        "tags": ["trending"],
        "amenities": ["Beach Walk", "Sunset", "Seafood"],
        "travel_tips": "The sunset crowd is heavy. Keep valuables close and choose seafood stalls with visible turnover.",
        "photos": [
            ("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1000", "Beach sunset"),
        ],
        "videos": [],
    },
    {
        "key": "puran-dhaka-kitchen",
        "author": "nadia",
        "name": "Puran Dhaka Kitchen",
        "category": "restaurant",
        "location": "Old Dhaka",
        "latitude": 23.7104,
        "longitude": 90.4074,
        "price_range": "budget",
        "tags": ["trending"],
        "amenities": ["Kacchi Biryani", "Takeaway", "Local Snacks"],
        "travel_tips": "Lunch hours are busiest. Try kacchi, borhani, and firni if you want the classic Old Dhaka food run.",
        "photos": [
            ("https://images.unsplash.com/photo-1697155406055-2db32d47ca07?q=80&w=1000", "Biryani spread"),
        ],
        "videos": [],
    },
    {
        "key": "grand-sultan",
        "author": "demo",
        "name": "Grand Sultan Tea Resort",
        "category": "hotel",
        "location": "Srimangal, Sylhet",
        "latitude": 24.3065,
        "longitude": 91.7296,
        "price_range": "premium",
        "tags": ["trending"],
        "amenities": ["WiFi", "AC", "Swimming Pool", "Tea Garden Tour", "Restaurant", "Spa"],
        "travel_tips": "Book a garden-view room if you want the full Srimangal feeling. Their tea tasting is worth planning around.",
        "photos": [
            ("https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?q=80&w=1000", "Resort in tea gardens"),
        ],
        "videos": [],
    },
    {
        "key": "hotel-sea-crown",
        "author": "ayesha",
        "name": "Hotel Sea Crown",
        "category": "hotel",
        "location": "Kalatali Road, Cox's Bazar",
        "latitude": 21.4272,
        "longitude": 91.9710,
        "price_range": "mid_range",
        "tags": ["trending"],
        "amenities": ["WiFi", "AC", "Room Service", "Sea View", "Restaurant"],
        "travel_tips": "Ask for a higher floor room for better sea views. It is convenient for Kalatali Beach walks.",
        "photos": [
            ("https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1000", "Hotel exterior"),
        ],
        "videos": [],
    },
    {
        "key": "nazmul-homestay",
        "author": "rafi",
        "name": "Nazmul's Beach Homestay",
        "category": "homestay",
        "location": "Laboni Point, Cox's Bazar",
        "latitude": 21.4317,
        "longitude": 91.9758,
        "price_range": "budget",
        "tags": ["hidden_gem"],
        "amenities": ["Fan", "Home-cooked Meals", "Local Guide"],
        "travel_tips": "Family-run and simple. Nazmul bhai can arrange early morning beach walks and local food recommendations.",
        "photos": [
            ("https://images.unsplash.com/photo-1587061949409-02df41d5e562?q=80&w=1000", "Simple homestay room"),
        ],
        "videos": [],
    },
    {
        "key": "nilgiri-resort",
        "author": "nadia",
        "name": "Nilgiri Hills Resort",
        "category": "hotel",
        "location": "Nilgiri, Bandarban",
        "latitude": 21.7830,
        "longitude": 92.3710,
        "price_range": "mid_range",
        "tags": ["trending"],
        "amenities": ["Restaurant", "Cloud View", "Parking", "Generator"],
        "travel_tips": "Cloud views are best after rain. Confirm road and security conditions before starting from Bandarban town.",
        "photos": [
            ("https://images.unsplash.com/photo-1596178065887-1198b6148b2b?q=80&w=1000", "Clouds below the resort"),
        ],
        "videos": [],
    },
    {
        "key": "sundarbans-camp",
        "author": "rafi",
        "name": "Sundarbans Tiger Camp",
        "category": "guesthouse",
        "location": "Khulna, Sundarbans Gateway",
        "latitude": 22.3216,
        "longitude": 89.1500,
        "price_range": "mid_range",
        "tags": ["trending"],
        "amenities": ["Boat Tour", "Nature Guide", "Meals Included", "Generator"],
        "travel_tips": "A useful base for permitted Sundarbans tours. Book a licensed guide and confirm forest permits in advance.",
        "photos": [
            ("https://images.unsplash.com/photo-1559827260-dc66d52bef19?q=80&w=1000", "Riverside camp"),
        ],
        "videos": [],
    },
    {
        "key": "chakma-homestay",
        "author": "nadia",
        "name": "Chakma Heritage Homestay",
        "category": "homestay",
        "location": "Rangamati Sadar",
        "latitude": 22.6320,
        "longitude": 92.1980,
        "price_range": "budget",
        "tags": ["hidden_gem"],
        "amenities": ["Traditional Meals", "Cultural Immersion", "Boat Ride"],
        "travel_tips": "A warm family stay with traditional food. Ask before taking portraits and respect local customs.",
        "photos": [
            ("https://images.unsplash.com/photo-1540541338287-41700207dee6?q=80&w=1000", "Lake-side home"),
        ],
        "videos": [],
    },
]


ITINERARIES = [
    {
        "key": "demo-sylhet",
        "user": "demo",
        "destination": "Sylhet",
        "duration_days": 3,
        "budget": 15000,
        "travel_style": "comfort",
        "interests": ["nature", "photography", "tea gardens", "waterfalls"],
        "group_type": "friends",
        "activities": [
            ("09:00", "11:00", 1, "Arrival and Hotel Check-in", "Check in and settle near Sylhet city before heading out.", 0, "Sylhet City", "rest", None),
            ("14:00", "17:30", 1, "Jaflong Riverside Visit", "Explore the river view and photograph the hills.", 900, "Jaflong", "sightseeing", "jaflong"),
            ("08:00", "13:00", 2, "Ratargul Boat Tour", "Take a small boat through the swamp forest.", 700, "Ratargul", "activity", "ratargul"),
            ("15:00", "17:00", 2, "Tea Garden Walk", "Slow walk through tea estates near Srimangal.", 300, "Srimangal", "sightseeing", "lawachara"),
            ("09:00", "12:00", 3, "Lawachara Forest Trail", "Guided forest walk with birdwatching.", 600, "Lawachara", "activity", "lawachara"),
        ],
    },
    {
        "key": "ayesha-cox",
        "user": "ayesha",
        "destination": "Cox's Bazar",
        "duration_days": 2,
        "budget": 12000,
        "travel_style": "budget",
        "interests": ["beaches", "seafood", "sunset"],
        "group_type": "couple",
        "activities": [
            ("15:30", "18:00", 1, "Laboni Beach Sunset", "Walk the beach and watch sunset from Laboni Point.", 0, "Laboni Beach", "sightseeing", "laboni"),
            ("19:00", "21:00", 1, "Seafood Dinner", "Try grilled fish near Kalatali.", 1500, "Kalatali", "food", None),
            ("08:00", "12:00", 2, "Inani Beach Drive", "Morning drive down Marine Drive toward Inani.", 1200, "Inani Beach", "activity", None),
        ],
    },
    {
        "key": "rafi-sylhet",
        "user": "rafi",
        "destination": "Sylhet",
        "duration_days": 4,
        "budget": 20000,
        "travel_style": "comfort",
        "interests": ["nature", "photography", "hiking", "tea gardens"],
        "group_type": "solo",
        "activities": [
            ("07:00", "10:00", 1, "Madhabkunda Waterfall", "Start early for waterfall photos.", 1200, "Moulvibazar", "sightseeing", None),
            ("08:30", "12:00", 2, "Ratargul Second Route", "Try a quieter boat route through the forest.", 800, "Ratargul", "activity", "ratargul"),
            ("14:00", "16:30", 2, "Srimangal Tea Estate", "Tea tasting and estate photography.", 500, "Srimangal", "sightseeing", "lawachara"),
            ("06:00", "09:00", 4, "Dawn Photography", "Soft light photography near tea gardens.", 200, "Srimangal", "activity", None),
        ],
    },
    {
        "key": "nadia-bandarban",
        "user": "nadia",
        "destination": "Bandarban",
        "duration_days": 3,
        "budget": 18000,
        "travel_style": "adventure",
        "interests": ["hiking", "mountains", "culture"],
        "group_type": "friends",
        "activities": [
            ("07:00", "12:00", 1, "Nilgiri Viewpoint", "Cloud view stop and short ridge walk.", 1500, "Nilgiri", "sightseeing", "nilgiri-resort"),
            ("09:00", "13:00", 2, "Golden Temple and Local Market", "Cultural visit and local snacks.", 600, "Bandarban Town", "culture", None),
            ("06:30", "11:30", 3, "Hill Trail Hike", "Guided hike on a nearby trail.", 1800, "Bandarban", "activity", None),
        ],
    },
]


TRANSIT_BLUEPRINTS = [
    {
        "key": "dhaka-sajek",
        "user": "demo",
        "origin": "Dhaka",
        "destination": "Sajek Valley",
        "raw_description": "Take a night coach from Dhaka to Khagrachhari, then share a Chander Gari jeep to Sajek after the checkpoint.",
        "estimated_duration_mins": 570,
        "estimated_cost_bdt": 1400,
        "notes": "Split jeep cost with other travelers. Avoid late departures because checkpoint timing matters.",
        "steps": [
            (1, "Take a night coach from Dhaka Fakirapool to Khagrachhari.", "bus", 420, 700),
            (2, "Find or reserve a shared Chander Gari jeep from Khagrachhari.", "car", 30, 0),
            (3, "Stop at Baghaichhari checkpoint with NID or passport ready.", "walking", 20, 0),
            (4, "Continue by jeep to Sajek Valley.", "car", 100, 700),
        ],
    },
    {
        "key": "sylhet-ratargul",
        "user": "rafi",
        "origin": "Sylhet City",
        "destination": "Ratargul Swamp Forest",
        "raw_description": "Take a CNG from Sylhet city to Salutikar, then hire a country boat into Ratargul.",
        "estimated_duration_mins": 150,
        "estimated_cost_bdt": 650,
        "notes": "Best from June to September. Bring waterproof shoes.",
        "steps": [
            (1, "Take a CNG from Zindabazar to Salutikar boat ghat.", "cng", 30, 150),
            (2, "Hire a wooden boat for the swamp forest loop.", "boat", 120, 500),
        ],
    },
    {
        "key": "dhaka-sundarbans",
        "user": "nadia",
        "origin": "Dhaka",
        "destination": "Sundarbans (Mongla Entry)",
        "raw_description": "Take an overnight launch from Sadarghat to Mongla, arrange permit and guide, then enter by boat.",
        "estimated_duration_mins": 780,
        "estimated_cost_bdt": 2700,
        "notes": "Do not enter the forest without a licensed guide.",
        "steps": [
            (1, "Reach Dhaka Sadarghat launch terminal before evening departure.", "rickshaw", 30, 50),
            (2, "Board overnight launch to Mongla.", "launch", 720, 1500),
            (3, "Get Sundarbans permit from the range office.", "walking", 15, 150),
            (4, "Join a licensed boat tour from Mongla jetty.", "boat", 15, 1000),
        ],
    },
    {
        "key": "srimangal-lawachara",
        "user": "ayesha",
        "origin": "Srimangal",
        "destination": "Lawachara National Park",
        "raw_description": "Hire a CNG from Srimangal town to Lawachara gate, then walk the marked forest trail.",
        "estimated_duration_mins": 45,
        "estimated_cost_bdt": 100,
        "notes": "Morning visits have the best chance of wildlife sightings.",
        "steps": [
            (1, "Hire a CNG from Srimangal bus stand to Lawachara gate.", "cng", 20, 80),
            (2, "Walk the main trail or hire a guide at the entrance.", "walking", 25, 20),
        ],
    },
]


EMERGENCY_FACILITIES = [
    ("dhaka-medical", "Dhaka Medical College Hospital", "hospital", "Secretariat Road, Dhaka 1000", "Dhaka", 23.7260, 90.3978, "02-55165088", "Largest public hospital in Bangladesh. 24/7 emergency department."),
    ("sylhet-osmani", "Sylhet MAG Osmani Medical College Hospital", "hospital", "Medical College Road, Sylhet 3100", "Sylhet", 24.8949, 91.8687, "0821-716970", "Main hospital for Sylhet division."),
    ("cox-sadar", "Cox's Bazar Sadar Hospital", "hospital", "Hospital Road, Cox's Bazar", "Cox's Bazar", 21.4354, 92.0058, "0341-63044", "Nearest major hospital for beach tourists."),
    ("rangamati-general", "Rangamati General Hospital", "hospital", "Hospital Road, Rangamati", "Rangamati", 22.6372, 92.1988, "0351-62053", "Main hospital for Rangamati Hill District."),
    ("khulna-medical", "Khulna Medical College Hospital", "hospital", "KDA Avenue, Khulna", "Khulna", 22.8098, 89.5644, "041-720062", "Primary hospital for Khulna division."),
    ("dhaka-police", "Dhaka Metropolitan Police HQ", "police_station", "36 Shahid Captain Mansur Ali Sarani, Dhaka", "Dhaka", 23.7372, 90.4059, "02-9556990", "Call 999 for emergencies."),
    ("sylhet-kotwali", "Sylhet Kotwali Police Station", "police_station", "East Dargah Gate, Sylhet", "Sylhet", 24.8963, 91.8712, "0821-714444", "Central police station in Sylhet city."),
    ("cox-tourist-police", "Tourist Police Cox's Bazar", "tourist_police", "Laboni Beach Point, Cox's Bazar", "Cox's Bazar", 21.4272, 91.9790, "01769-690731", "Beach patrol and tourist assistance."),
    ("sylhet-tourist-police", "Tourist Police Sylhet", "tourist_police", "Jindabazar, Sylhet", "Sylhet", 24.8994, 91.8710, "01769-690732", "Covers Ratargul, Jaflong, and Srimangal areas."),
    ("khulna-tourist-police", "Tourist Police Khulna", "tourist_police", "KDA Avenue, Khulna", "Khulna", 22.8200, 89.5500, "01769-690734", "Covers Sundarbans entry points."),
]


def ensure_tables_exist() -> None:
    required = {
        "users",
        "community_entries",
        "entry_photos",
        "entry_video_embeds",
        "entry_reviews",
        "entry_review_photos",
        "nomad_metrics",
        "itineraries",
        "itinerary_activities",
        "group_trips",
        "group_trip_members",
        "group_trip_budgets",
        "group_trip_expenses",
        "group_activities",
        "polls",
        "poll_options",
        "poll_votes",
        "transit_blueprints",
        "transit_blueprint_steps",
        "transit_fare_contributions",
        "emergency_facilities",
        "user_locations",
        "buddy_matches",
    }
    existing = set(inspect(engine).get_table_names())
    missing = sorted(required - existing)
    if missing:
        raise RuntimeError(
            "Missing tables: "
            + ", ".join(missing)
            + ". Run `uv run alembic upgrade head` before seeding."
        )


def delete_if_ids(db, model, column, ids: list[uuid.UUID]) -> None:
    if ids:
        db.query(model).filter(column.in_(ids)).delete(synchronize_session=False)


def upsert_users(db) -> dict[str, User]:
    users: dict[str, User] = {}
    for data in USERS:
        user = (
            db.query(User)
            .filter(or_(User.email == data["email"], User.google_id == data["google_id"]))
            .first()
        )
        if not user:
            user = User(
                id=seed_id("user", data["key"]),
                google_id=data["google_id"],
                email=data["email"],
                name=data["name"],
                picture_url=data["picture_url"],
                role="user",
                is_active=True,
            )
            db.add(user)
        else:
            user.google_id = data["google_id"]
            user.email = data["email"]
            user.name = data["name"]
            user.picture_url = data["picture_url"]
            user.role = "user"
            user.is_active = True
        users[data["key"]] = user
    db.flush()
    return users


def clear_seed_content(db, users: dict[str, User]) -> None:
    user_ids = [user.id for user in users.values()]
    entry_ids = seed_ids("entry", [item["key"] for item in COMMUNITY_ENTRIES])
    itinerary_ids = seed_ids("itinerary", [item["key"] for item in ITINERARIES])
    group_ids = seed_ids("group_trip", ["sylhet-crew", "cox-weekend", "bandarban-trek"])
    poll_ids = seed_ids("poll", ["sylhet-hotel", "cox-dinner"])
    blueprint_ids = seed_ids("transit_blueprint", [item["key"] for item in TRANSIT_BLUEPRINTS])
    fare_ids = seed_ids("transit_fare", [
        "dhaka-sylhet-bus-1",
        "dhaka-sylhet-bus-2",
        "dhaka-sylhet-train-1",
        "sylhet-ratargul-cng-1",
        "sylhet-ratargul-cng-2",
        "dhaka-cox-bus-1",
        "dhaka-cox-bus-2",
        "dhaka-khulna-train-1",
    ])
    emergency_ids = seed_ids("emergency", [item[0] for item in EMERGENCY_FACILITIES])
    review_ids = seed_ids("entry_review", [
        "ratargul-ayesha",
        "jaflong-demo",
        "lawachara-rafi",
        "sajek-nadia",
        "laboni-demo",
        "grand-sultan-ayesha",
        "hotel-sea-crown-rafi",
        "nilgiri-demo",
    ])

    existing_group_ids = [
        row[0]
        for row in db.query(GroupTrip.id)
        .filter(or_(GroupTrip.id.in_(group_ids), GroupTrip.creator_id.in_(user_ids)))
        .all()
    ]
    existing_poll_ids = [
        row[0]
        for row in db.query(Poll.id)
        .filter(or_(Poll.id.in_(poll_ids), Poll.trip_id.in_(existing_group_ids)))
        .all()
    ]
    delete_if_ids(db, Vote, Vote.poll_id, existing_poll_ids)
    delete_if_ids(db, PollOption, PollOption.poll_id, existing_poll_ids)
    delete_if_ids(db, Poll, Poll.id, existing_poll_ids)
    delete_if_ids(db, GroupActivity, GroupActivity.trip_id, existing_group_ids)
    delete_if_ids(db, GroupTripExpense, GroupTripExpense.trip_id, existing_group_ids)
    delete_if_ids(db, GroupTripBudget, GroupTripBudget.trip_id, existing_group_ids)
    delete_if_ids(db, GroupTripMember, GroupTripMember.trip_id, existing_group_ids)
    delete_if_ids(db, GroupTrip, GroupTrip.id, existing_group_ids)

    existing_review_ids = [
        row[0]
        for row in db.query(EntryReview.id)
        .filter(
            or_(
                EntryReview.id.in_(review_ids),
                EntryReview.entry_id.in_(entry_ids),
                EntryReview.user_id.in_(user_ids),
            )
        )
        .all()
    ]
    delete_if_ids(db, EntryReviewPhoto, EntryReviewPhoto.review_id, existing_review_ids)
    delete_if_ids(db, EntryReview, EntryReview.id, existing_review_ids)

    existing_itinerary_ids = [
        row[0]
        for row in db.query(Itinerary.id)
        .filter(or_(Itinerary.id.in_(itinerary_ids), Itinerary.user_id.in_(user_ids)))
        .all()
    ]
    delete_if_ids(db, ItineraryActivity, ItineraryActivity.itinerary_id, existing_itinerary_ids)
    delete_if_ids(db, Itinerary, Itinerary.id, existing_itinerary_ids)

    delete_if_ids(db, NomadMetric, NomadMetric.entry_id, entry_ids)
    db.query(NomadMetric).filter(NomadMetric.user_id.in_(user_ids)).delete(
        synchronize_session=False
    )
    delete_if_ids(db, EntryVideoEmbed, EntryVideoEmbed.entry_id, entry_ids)
    delete_if_ids(db, EntryPhoto, EntryPhoto.entry_id, entry_ids)
    delete_if_ids(db, CommunityEntry, CommunityEntry.id, entry_ids)

    delete_if_ids(db, TransitBlueprintStep, TransitBlueprintStep.blueprint_id, blueprint_ids)
    delete_if_ids(db, TransitBlueprint, TransitBlueprint.id, blueprint_ids)
    delete_if_ids(db, TransitFareContribution, TransitFareContribution.id, fare_ids)
    delete_if_ids(db, EmergencyFacility, EmergencyFacility.id, emergency_ids)

    db.query(UserLocation).filter(UserLocation.user_id.in_(user_ids)).delete(
        synchronize_session=False
    )
    db.query(BuddyMatch).filter(
        or_(BuddyMatch.user_id.in_(user_ids), BuddyMatch.matched_user_id.in_(user_ids))
    ).delete(synchronize_session=False)

    db.flush()


def seed_community(db, users: dict[str, User]) -> dict[str, CommunityEntry]:
    entries: dict[str, CommunityEntry] = {}
    for data in COMMUNITY_ENTRIES:
        entry = CommunityEntry(
            id=seed_id("entry", data["key"]),
            user_id=users[data["author"]].id,
            category=data["category"],
            name=data["name"],
            location=data["location"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            price_range=data["price_range"],
            amenities=data["amenities"],
            travel_tips=data["travel_tips"],
            tags=data["tags"],
        )
        db.add(entry)
        entries[data["key"]] = entry

        for idx, (url, caption) in enumerate(data["photos"], start=1):
            db.add(
                EntryPhoto(
                    id=seed_id("entry_photo", f"{data['key']}:{idx}"),
                    entry_id=entry.id,
                    url=url,
                    public_id=f"final_seed/{data['key']}/{idx}",
                    caption=caption,
                )
            )
        for idx, (url, platform) in enumerate(data["videos"], start=1):
            db.add(
                EntryVideoEmbed(
                    id=seed_id("entry_video", f"{data['key']}:{idx}"),
                    entry_id=entry.id,
                    url=url,
                    platform=platform,
                )
            )
    db.flush()
    return entries


def seed_nomad_metrics(db, users: dict[str, User], entries: dict[str, CommunityEntry]) -> None:
    rows = [
        ("ratargul", "demo", "GP", "4G", 5, True),
        ("ratargul", "ayesha", "Robi", "4G", 4, True),
        ("jaflong", "rafi", "Banglalink", "3G", 4, True),
        ("lawachara", "nadia", "GP", "4G", 5, False),
        ("sajek", "demo", "Robi", "3G", 4, False),
        ("laboni", "ayesha", "GP", "5G", 4, True),
        ("grand-sultan", "rafi", "GP", "4G", 5, True),
        ("nilgiri-resort", "nadia", "Teletalk", "2G", 4, False),
    ]
    for entry_key, user_key, carrier, signal, safety, bkash in rows:
        db.add(
            NomadMetric(
                id=seed_id("nomad_metric", f"{entry_key}:{user_key}"),
                entry_id=entries[entry_key].id,
                user_id=users[user_key].id,
                carrier=carrier,
                signal_strength=signal,
                safety_rating=safety,
                bkash_available=bkash,
            )
        )
    db.flush()


def seed_itineraries(
    db, users: dict[str, User], entries: dict[str, CommunityEntry]
) -> tuple[dict[str, Itinerary], dict[str, ItineraryActivity]]:
    itineraries: dict[str, Itinerary] = {}
    activities: dict[str, ItineraryActivity] = {}
    for data in ITINERARIES:
        itinerary = Itinerary(
            id=seed_id("itinerary", data["key"]),
            user_id=users[data["user"]].id,
            destination=data["destination"],
            duration_days=data["duration_days"],
            budget=data["budget"],
            travel_style=data["travel_style"],
            interests=data["interests"],
            group_type=data["group_type"],
        )
        db.add(itinerary)
        itineraries[data["key"]] = itinerary

        for idx, item in enumerate(data["activities"], start=1):
            start, end, day, title, description, cost, location, category, entry_key = item
            activity_key = f"{data['key']}:{idx}"
            activity = ItineraryActivity(
                id=seed_id("activity", activity_key),
                itinerary_id=itinerary.id,
                day_number=day,
                start_time=start,
                end_time=end,
                title=title,
                description=description,
                estimated_cost=cost,
                location=location,
                category=category,
                community_entry_id=entries[entry_key].id if entry_key else None,
            )
            db.add(activity)
            activities[activity_key] = activity
    db.flush()
    return itineraries, activities


def seed_reviews(
    db,
    users: dict[str, User],
    entries: dict[str, CommunityEntry],
    itineraries: dict[str, Itinerary],
    activities: dict[str, ItineraryActivity],
) -> None:
    rows = [
        ("ratargul-ayesha", "ratargul", "ayesha", 5, "budget", 700, 240, "Magical during monsoon. Boatmen were helpful and the forest felt calm in the morning.", "demo-sylhet", "demo-sylhet:3"),
        ("jaflong-demo", "jaflong", "demo", 4, "family", 1200, 180, "Great views and easy to combine with nearby Sylhet spots. Go before noon for fewer crowds.", "demo-sylhet", "demo-sylhet:2"),
        ("lawachara-rafi", "lawachara", "rafi", 5, "adventure", 600, 180, "A guide made the trail much better. We saw birds and heard gibbons deeper inside.", "rafi-sylhet", "rafi-sylhet:3"),
        ("sajek-nadia", "sajek", "nadia", 5, "adventure", 4500, 300, "The jeep ride is rough but the views are worth it. Carry cash and warm clothes.", None, None),
        ("laboni-demo", "laboni", "demo", 4, "budget", 500, 150, "Classic Cox's Bazar sunset spot. Crowded but lively and easy for first-time visitors.", "ayesha-cox", "ayesha-cox:1"),
        ("grand-sultan-ayesha", "grand-sultan", "ayesha", 5, "luxury", 12000, 240, "Polished service and a relaxing tea garden setting. Best for comfort-focused trips.", None, None),
        ("hotel-sea-crown-rafi", "hotel-sea-crown", "rafi", 4, "family", 4200, 120, "Convenient location and sea-facing rooms are worth requesting.", None, None),
        ("nilgiri-demo", "nilgiri-resort", "demo", 4, "adventure", 3500, 180, "Cloud views are excellent after rain. Road conditions need checking in advance.", "nadia-bandarban", "nadia-bandarban:1"),
    ]
    for key, entry_key, user_key, rating, style, cost, minutes, text, itinerary_key, activity_key in rows:
        review = EntryReview(
            id=seed_id("entry_review", key),
            entry_id=entries[entry_key].id,
            user_id=users[user_key].id,
            rating=rating,
            travel_style=style,
            actual_cost_bdt=cost,
            time_spent_minutes=minutes,
            review_text=text,
            itinerary_id=itineraries[itinerary_key].id if itinerary_key else None,
            activity_id=activities[activity_key].id if activity_key else None,
        )
        db.add(review)
        db.add(
            EntryReviewPhoto(
                id=seed_id("entry_review_photo", key),
                review_id=review.id,
                url="https://images.unsplash.com/photo-1472396961693-142e6e269027?q=80&w=1000",
                public_id=f"final_seed/reviews/{key}",
                caption="Seeded traveler photo",
            )
        )
    db.flush()


def seed_transit_blueprints(db, users: dict[str, User]) -> None:
    for data in TRANSIT_BLUEPRINTS:
        blueprint = TransitBlueprint(
            id=seed_id("transit_blueprint", data["key"]),
            user_id=users[data["user"]].id,
            origin=data["origin"],
            destination=data["destination"],
            raw_description=data["raw_description"],
            estimated_duration_mins=data["estimated_duration_mins"],
            estimated_cost_bdt=data["estimated_cost_bdt"],
            notes=data["notes"],
        )
        db.add(blueprint)
        for step_number, instruction, mode, duration, cost in data["steps"]:
            db.add(
                TransitBlueprintStep(
                    id=seed_id("transit_step", f"{data['key']}:{step_number}"),
                    blueprint_id=blueprint.id,
                    step_number=step_number,
                    instruction=instruction,
                    mode=mode,
                    estimated_duration_mins=duration,
                    estimated_cost_bdt=cost,
                )
            )
    db.flush()


def seed_transit_fares(db, users: dict[str, User]) -> None:
    rows = [
        ("dhaka-sylhet-bus-1", "demo", "Dhaka", "Sylhet", "bus", 700, 650, 850, "Night coach from Fakirapool.", "booked", date(2026, 3, 12)),
        ("dhaka-sylhet-bus-2", "rafi", "Dhaka", "Sylhet", "bus", 800, 700, 900, "Weekend fare was slightly higher.", "observed", date(2026, 4, 5)),
        ("dhaka-sylhet-train-1", "ayesha", "Dhaka", "Sylhet", "train", 520, 375, 720, "Intercity train seat fare range.", "quoted", date(2026, 2, 18)),
        ("sylhet-ratargul-cng-1", "demo", "Sylhet City", "Ratargul", "cng", 350, 300, 450, "Reserve CNG to boat ghat.", "observed", date(2026, 4, 2)),
        ("sylhet-ratargul-cng-2", "nadia", "Sylhet City", "Ratargul", "cng", 400, 350, 500, "Rainy day quote.", "quoted", date(2026, 4, 7)),
        ("dhaka-cox-bus-1", "ayesha", "Dhaka", "Cox's Bazar", "bus", 1200, 1000, 1600, "AC coach fare.", "booked", date(2026, 1, 22)),
        ("dhaka-cox-bus-2", "rafi", "Dhaka", "Cox's Bazar", "bus", 1000, 900, 1300, "Non-AC to AC range.", "observed", date(2026, 3, 3)),
        ("dhaka-khulna-train-1", "nadia", "Dhaka", "Khulna", "train", 650, 505, 950, "Sundarbans gateway route.", "quoted", date(2026, 2, 2)),
    ]
    for key, user_key, origin, destination, mode, fare, min_fare, max_fare, notes, source, travel_date in rows:
        db.add(
            TransitFareContribution(
                id=seed_id("transit_fare", key),
                user_id=users[user_key].id,
                origin=origin,
                destination=destination,
                mode=mode,
                fare_bdt=fare,
                min_fare_bdt=min_fare,
                max_fare_bdt=max_fare,
                notes=notes,
                source_type=source,
                travel_date=travel_date,
            )
        )
    db.flush()


def seed_emergency(db) -> None:
    for key, name, facility_type, address, district, lat, lng, phone, notes in EMERGENCY_FACILITIES:
        db.add(
            EmergencyFacility(
                id=seed_id("emergency", key),
                name=name,
                facility_type=facility_type,
                address=address,
                district=district,
                latitude=lat,
                longitude=lng,
                phone_number=phone,
                notes=notes,
            )
        )
    db.flush()


def seed_user_locations(db, users: dict[str, User]) -> None:
    rows = [
        ("demo", 24.8949, 91.8687, "traveling", "Exploring Sylhet tea country this week."),
        ("ayesha", 21.4272, 91.9710, "planning", "Planning a Cox's Bazar weekend."),
        ("rafi", 24.3065, 91.7296, "traveling", "In Srimangal for tea gardens and trails."),
        ("nadia", 22.1953, 92.2184, "planning", "Looking for Bandarban hiking buddies."),
    ]
    for user_key, lat, lng, status, message in rows:
        db.add(
            UserLocation(
                user_id=users[user_key].id,
                latitude=lat,
                longitude=lng,
                status=status,
                message=message,
            )
        )
    db.flush()


def seed_group_trips(
    db, users: dict[str, User], itineraries: dict[str, Itinerary], activities: dict[str, ItineraryActivity]
) -> None:
    trips = [
        ("sylhet-crew", "demo", "Sylhet Monsoon Crew", "Sylhet", "Boat rides, tea gardens, and flexible photo stops.", date(2026, 7, 10), date(2026, 7, 13), "public", "SYLHET2026", "demo-sylhet"),
        ("cox-weekend", "ayesha", "Cox's Bazar Weekend", "Cox's Bazar", "Budget beach weekend with seafood and sunset walks.", date(2026, 5, 16), date(2026, 5, 18), "public", "COXWEEKEND26", "ayesha-cox"),
        ("bandarban-trek", "nadia", "Bandarban Ridge Trek", "Bandarban", "Private small-group hill trek and cultural stops.", date(2026, 11, 5), date(2026, 11, 8), "private", "BANDARBAN26", "nadia-bandarban"),
    ]
    for key, creator, title, destination, description, start, end, visibility, invite, itinerary_key in trips:
        db.add(
            GroupTrip(
                id=seed_id("group_trip", key),
                creator_id=users[creator].id,
                title=title,
                destination=destination,
                description=description,
                start_date=start,
                end_date=end,
                visibility=visibility,
                invite_code=invite,
                itinerary_id=itineraries[itinerary_key].id,
            )
        )

    memberships = [
        ("sylhet-crew", "demo", "owner"),
        ("sylhet-crew", "rafi", "member"),
        ("sylhet-crew", "ayesha", "member"),
        ("cox-weekend", "ayesha", "owner"),
        ("cox-weekend", "demo", "member"),
        ("bandarban-trek", "nadia", "owner"),
        ("bandarban-trek", "rafi", "member"),
    ]
    for group_key, user_key, role in memberships:
        db.add(
            GroupTripMember(
                id=seed_id("group_member", f"{group_key}:{user_key}"),
                trip_id=seed_id("group_trip", group_key),
                user_id=users[user_key].id,
                role=role,
            )
        )

    budgets = [
        ("sylhet-crew", "demo", 45000),
        ("cox-weekend", "ayesha", 18000),
        ("bandarban-trek", "nadia", 55000),
    ]
    for group_key, user_key, amount in budgets:
        db.add(
            GroupTripBudget(
                id=seed_id("group_budget", group_key),
                trip_id=seed_id("group_trip", group_key),
                created_by_user_id=users[user_key].id,
                total_budget=amount,
                currency="BDT",
                alert_80_sent=False,
                alert_100_sent=False,
            )
        )

    expenses = [
        ("sylhet-crew:bus", "sylhet-crew", "demo", 7200, "transport", "Advance bus tickets", datetime(2026, 7, 10, 8, 0)),
        ("sylhet-crew:boat", "sylhet-crew", "rafi", 2400, "activity", "Ratargul boat booking", datetime(2026, 7, 11, 9, 30)),
        ("cox-weekend:hotel", "cox-weekend", "ayesha", 6500, "lodging", "Two nights near Kalatali", datetime(2026, 5, 16, 13, 0)),
        ("bandarban-trek:jeep", "bandarban-trek", "nadia", 9000, "transport", "Jeep reservation", datetime(2026, 11, 5, 7, 30)),
    ]
    for key, group_key, user_key, amount, category, note, spent_at in expenses:
        db.add(
            GroupTripExpense(
                id=seed_id("group_expense", key),
                trip_id=seed_id("group_trip", group_key),
                user_id=users[user_key].id,
                amount=amount,
                currency="BDT",
                category=category,
                note=note,
                spent_at=spent_at,
            )
        )

    polls = [
        ("sylhet-hotel", "sylhet-crew", "demo", "Where should we stay in Sylhet?", "Vote based on comfort and access to tea gardens.", True),
        ("cox-dinner", "cox-weekend", "ayesha", "Dinner plan for night one?", "Pick the first shared dinner spot.", True),
    ]
    for key, group_key, creator, title, description, is_active in polls:
        db.add(
            Poll(
                id=seed_id("poll", key),
                trip_id=seed_id("group_trip", group_key),
                creator_id=users[creator].id,
                title=title,
                description=description,
                is_active=is_active,
            )
        )

    poll_options = [
        ("sylhet-hotel", "grand-sultan", "Grand Sultan Tea Resort", "grand-sultan"),
        ("sylhet-hotel", "city-hotel", "Stay in Sylhet city", None),
        ("sylhet-hotel", "budget-homestay", "Budget homestay near Srimangal", None),
        ("cox-dinner", "seafood", "Kalatali seafood dinner", None),
        ("cox-dinner", "local", "Local rice and bhorta meal", None),
    ]
    for poll_key, option_key, text, activity_hint in poll_options:
        linked_activity = None
        if activity_hint == "grand-sultan":
            linked_activity = activities.get("demo-sylhet:4")
        db.add(
            PollOption(
                id=seed_id("poll_option", f"{poll_key}:{option_key}"),
                poll_id=seed_id("poll", poll_key),
                text=text,
                image_url=None,
                itinerary_activity_id=linked_activity.id if linked_activity else None,
            )
        )

    votes = [
        ("sylhet-hotel", "grand-sultan", "demo"),
        ("sylhet-hotel", "grand-sultan", "ayesha"),
        ("sylhet-hotel", "budget-homestay", "rafi"),
        ("cox-dinner", "seafood", "ayesha"),
        ("cox-dinner", "seafood", "demo"),
    ]
    for poll_key, option_key, user_key in votes:
        db.add(
            Vote(
                id=seed_id("vote", f"{poll_key}:{user_key}"),
                poll_id=seed_id("poll", poll_key),
                poll_option_id=seed_id("poll_option", f"{poll_key}:{option_key}"),
                user_id=users[user_key].id,
            )
        )

    activities_feed = [
        ("sylhet-crew:created", "sylhet-crew", "demo", "itinerary_linked", "linked a shared itinerary to the trip", {"itinerary_id": str(itineraries["demo-sylhet"].id)}),
        ("sylhet-crew:poll", "sylhet-crew", "demo", "poll_created", "started a new poll: Where should we stay in Sylhet?", {"poll_id": str(seed_id("poll", "sylhet-hotel"))}),
        ("sylhet-crew:vote", "sylhet-crew", "rafi", "voted", "voted for 'Budget homestay near Srimangal' in poll: Where should we stay in Sylhet?", {"poll_id": str(seed_id("poll", "sylhet-hotel"))}),
        ("cox-weekend:poll", "cox-weekend", "ayesha", "poll_created", "started a new poll: Dinner plan for night one?", {"poll_id": str(seed_id("poll", "cox-dinner"))}),
    ]
    for key, group_key, user_key, activity_type, description, metadata in activities_feed:
        db.add(
            GroupActivity(
                id=seed_id("group_activity", key),
                trip_id=seed_id("group_trip", group_key),
                user_id=users[user_key].id,
                activity_type=activity_type,
                description=description,
                metadata_json=metadata,
            )
        )
    db.flush()


def seed_buddy_matches(db, users: dict[str, User]) -> None:
    rows = [
        ("demo-rafi", "demo", "rafi", 0.86, ["nature", "photography", "tea gardens"], ["Sylhet"], "accepted", "demo"),
        ("rafi-demo", "rafi", "demo", 0.86, ["nature", "photography", "tea gardens"], ["Sylhet"], "accepted", "demo"),
        ("ayesha-demo", "ayesha", "demo", 0.48, ["beaches", "sunset"], ["Cox's Bazar"], "suggested", None),
        ("nadia-rafi", "nadia", "rafi", 0.42, ["hiking"], ["Bandarban"], "pending", "nadia"),
    ]
    for key, user_key, matched_key, score, interests, destinations, status, initiated_by in rows:
        db.add(
            BuddyMatch(
                id=seed_id("buddy_match", key),
                user_id=users[user_key].id,
                matched_user_id=users[matched_key].id,
                match_score=score,
                common_interests=interests,
                common_destinations=destinations,
                status=status,
                initiated_by=users[initiated_by].id if initiated_by else None,
            )
        )
    db.flush()


def seed_all() -> None:
    ensure_tables_exist()
    db = SessionLocal()
    try:
        users = upsert_users(db)
        clear_seed_content(db, users)

        entries = seed_community(db, users)
        seed_nomad_metrics(db, users, entries)
        itineraries, activities = seed_itineraries(db, users, entries)
        seed_reviews(db, users, entries, itineraries, activities)
        seed_transit_blueprints(db, users)
        seed_transit_fares(db, users)
        seed_emergency(db)
        seed_user_locations(db, users)
        seed_group_trips(db, users, itineraries, activities)
        seed_buddy_matches(db, users)

        db.commit()
        print("Final seed completed successfully.")
        print(f"Users: {len(USERS)}")
        print(f"Community entries: {len(COMMUNITY_ENTRIES)}")
        print(f"Itineraries: {len(ITINERARIES)}")
        print(f"Transit blueprints: {len(TRANSIT_BLUEPRINTS)}")
        print(f"Emergency facilities: {len(EMERGENCY_FACILITIES)}")
        print("Seed users:")
        for user in USERS:
            print(f"  - {user['email']} ({user['name']})")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
