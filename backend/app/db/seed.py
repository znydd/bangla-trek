import logging
import uuid
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.place import Place, PlaceAlias, PlaceTag, PlaceMedia
from app.models.review import Review, ReviewPaymentMethod
from app.models.trip import TravelTrip, TravelTripRequirement, TravelTripMember
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_database():
    db: Session = SessionLocal()
    try:
        # 1. Create seed users if not existing
        admin_user = db.query(User).filter(User.email == "admin@banglatrek.com").first()
        if not admin_user:
            admin_user = User(
                id=uuid.uuid4(),
                google_id="seed_admin_google_id",
                email="admin@banglatrek.com",
                name="Bangla Trek Research Team",
                picture_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb",
                role="admin",
                email_verified=True,
            )
            db.add(admin_user)

        traveler_user1 = db.query(User).filter(User.email == "rumana@example.com").first()
        if not traveler_user1:
            traveler_user1 = User(
                id=uuid.uuid4(),
                google_id="seed_rumana_google_id",
                email="rumana@example.com",
                name="Rumana Sultana",
                picture_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330",
                role="user",
                email_verified=True,
            )
            db.add(traveler_user1)

        traveler_user2 = db.query(User).filter(User.email == "tanvir@example.com").first()
        if not traveler_user2:
            traveler_user2 = User(
                id=uuid.uuid4(),
                google_id="seed_tanvir_google_id",
                email="tanvir@example.com",
                name="Tanvir Hasan",
                picture_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",
                role="user",
                email_verified=True,
            )
            db.add(traveler_user2)

        traveler_user3 = db.query(User).filter(User.email == "nabila@example.com").first()
        if not traveler_user3:
            traveler_user3 = User(
                id=uuid.uuid4(),
                google_id="seed_nabila_google_id",
                email="nabila@example.com",
                name="Nabila Rahman",
                picture_url="https://images.unsplash.com/photo-1517841905240-472988babdf9",
                role="user",
                email_verified=True,
            )
            db.add(traveler_user3)

        db.commit()

        # 2. Seed 6 rich Bangladesh Places
        places_data = [
            {
                "slug": "debotakhum-bandarbans-river-canyon",
                "name": "Debotakhum",
                "normalized_name": "debotakhum",
                "category": "Nature & adventure",
                "summary": "A quiet river-and-canyon journey through the green hills of Bandarban, reached by local transport, boat and a short trek.",
                "description": "Debotakhum is a narrow khum in Rowangchhari where steep green walls rise above still water. The journey is part of the experience: travelers pass hill settlements, take a small boat and walk through changing terrain before reaching the canyon.",
                "village": "Shilbandha Para",
                "upazila": "Rowangchhari",
                "district": "Bandarban",
                "division": "Chattogram",
                "nearest_hub": "Bandarban town",
                "latitude": 22.2326,
                "longitude": 92.3029,
                "best_season": "November–January",
                "suggested_duration": "2 days / 1 night",
                "guide_requirement": "Local guide recommended",
                "budget_min_bdt": 3800.0,
                "budget_max_bdt": 6200.0,
                "highlights": [
                    "A peaceful boat ride into a narrow green canyon",
                    "A journey through Rowangchhari and nearby hill settlements",
                    "Less commercial than Bandarban's best-known attractions",
                    "A rewarding mix of local transport, walking and water travel"
                ],
                "know_before_you_go": [
                    "Access can become unsafe after heavy rain; confirm conditions locally.",
                    "Carry cash because digital payment and ATM access are inconsistent.",
                    "Start early so the return journey is completed before dark.",
                    "Mobile coverage becomes intermittent after leaving Rowangchhari.",
                    "Respect local communities and confirm photography permission when appropriate."
                ],
                "tags": ["Hidden Gem", "River Journey", "Adventure", "Canyon"],
                "aliases": ["Debotakhum Canyon", "Rowangchhari Khum"],
                "media": [
                    {"media_type": "photo", "url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb", "caption": "River canyon and hill landscape"}
                ],
                "reviews": [
                    {
                        "user": traveler_user1,
                        "rating": 5,
                        "visited_on": date(2026, 1, 18),
                        "travel_style": "adventure",
                        "group_type": "Friends",
                        "group_size": 5,
                        "starting_location": "Dhaka",
                        "actual_cost_bdt": 4600.0,
                        "travel_guide": "We took an overnight AC bus from Dhaka for ৳1,800 each, then reserved a jeep from Bandarban to Rowangchhari for ৳1,500 total. Five of us shared a local boat and guide, and the final walk took around 45 minutes.",
                        "crowd_level": "Light crowd",
                        "access_difficulty": "Moderate",
                        "road_condition": "Boat and walking",
                        "pm_methods": ["Cash", "bKash"],
                        "mobile_carrier": "GP",
                        "strongest_network": "4G",
                        "network_reliability": "Intermittent",
                        "safety": "Mostly safe",
                        "cleanliness": "Clean",
                    },
                    {
                        "user": traveler_user2,
                        "rating": 4,
                        "visited_on": date(2025, 12, 6),
                        "travel_style": "budget",
                        "group_type": "Friends",
                        "group_size": 4,
                        "starting_location": "Chattogram",
                        "actual_cost_bdt": 3200.0,
                        "travel_guide": "From Chattogram we took a local bus to Bandarban and another local vehicle toward Rowangchhari. Four of us negotiated one boat-and-guide package. Try to arrive before noon.",
                        "crowd_level": "Busy",
                        "access_difficulty": "Moderate",
                        "road_condition": "Rough",
                        "pm_methods": ["Cash"],
                        "mobile_carrier": "Robi",
                        "strongest_network": "3G",
                        "network_reliability": "Limited areas",
                        "safety": "Mostly safe",
                        "cleanliness": "Okay",
                    }
                ]
            },
            {
                "slug": "sajek-valley-cloud-resorts",
                "name": "Sajek Valley",
                "normalized_name": "sajek-valley",
                "category": "Hill Station",
                "summary": "Famous for sunrise above clouds, lush green Kasalong hills, and quiet Ruilui indigenous settlements.",
                "description": "Sajek Valley is an emerging tourist spot in Bangladesh situated among the hills of Kasalong range of mountains in Sajek union, Baghaichhari Upazila in Rangamati District. Known as the Queen of Hills.",
                "village": "Ruilui Para",
                "upazila": "Baghaichhari",
                "district": "Rangamati",
                "division": "Chattogram",
                "nearest_hub": "Khagrachari Bus Stand",
                "latitude": 23.3820,
                "longitude": 92.2938,
                "best_season": "October–March",
                "suggested_duration": "3 days / 2 nights",
                "guide_requirement": "Army escort required from Dighinala",
                "budget_min_bdt": 4500.0,
                "budget_max_bdt": 8500.0,
                "highlights": [
                    "Ruilui Para morning cloud horizon",
                    "Konglak Hill highest viewpoint walk",
                    "Chander Gari safari through hilly roads",
                    "Traditional bamboo chicken dinner"
                ],
                "know_before_you_go": [
                    "Army escorts leave Dighinala strictly at 10 AM and 3 PM.",
                    "Book resorts in Ruilui Para at least 2 weeks in advance.",
                    "Electricity is mostly solar/generator driven; bring power banks.",
                    "Carry cash as there are no digital ATM booths in the valley."
                ],
                "tags": ["Hill Station", "Clouds", "Resorts", "Viewpoint"],
                "aliases": ["Ruilui Para", "Konglak Pahar", "Sajek"],
                "media": [
                    {"media_type": "photo", "url": "https://images.unsplash.com/photo-1585123334904-845d60e97b29", "caption": "Clouds floating below Ruilui Para resorts"}
                ],
                "reviews": [
                    {
                        "user": traveler_user3,
                        "rating": 5,
                        "visited_on": date(2026, 2, 1),
                        "travel_style": "comfort",
                        "group_type": "Couple",
                        "group_size": 2,
                        "starting_location": "Dhaka",
                        "actual_cost_bdt": 7200.0,
                        "travel_guide": "Watching the clouds float right under our balcony at Ruilui Para was magical! Take the night bus from Dhaka to Khagrachari, then hire a Chander Gari for ৳6,000 round trip.",
                        "crowd_level": "Busy",
                        "access_difficulty": "Easy",
                        "road_condition": "Paved",
                        "pm_methods": ["Cash", "bKash"],
                        "mobile_carrier": "GP",
                        "strongest_network": "4G",
                        "network_reliability": "Stable",
                        "safety": "Very safe",
                        "cleanliness": "Clean",
                    }
                ]
            },
            {
                "slug": "nilgiri-bandarban-peak",
                "name": "Nilgiri Resort",
                "normalized_name": "nilgiri-resort",
                "category": "Hill Station",
                "summary": "One of the highest resort peaks in Bangladesh managed by the Army, standing at 2200ft above sea level.",
                "description": "Nilgiri is located in Thanchi Upazila of Bandarban. Perched atop high mountain ridges, travelers can touch floating clouds and observe panoramic views of Bandarban hill tracts.",
                "village": "Thanchi Road",
                "upazila": "Thanchi",
                "district": "Bandarban",
                "division": "Chattogram",
                "nearest_hub": "Bandarban Sadar",
                "latitude": 21.9213,
                "longitude": 92.3278,
                "best_season": "September–February",
                "suggested_duration": "2 days / 1 night",
                "guide_requirement": "Not required for day trip",
                "budget_min_bdt": 5000.0,
                "budget_max_bdt": 9500.0,
                "highlights": [
                    "2200ft high cloud peak view",
                    "Shailopropat Waterfall stop on the way",
                    "Chimbuk Hill viewpoint",
                    "Sunset above mountain clouds"
                ],
                "know_before_you_go": [
                    "Cottage bookings must be reserved well in advance via Army officer reference or booking desk.",
                    "Mountain road has sharp curves; carry motion sickness medication.",
                    "Entry fee applies for day tourists."
                ],
                "tags": ["Bandarban", "Peak", "Views", "Army Resort"],
                "aliases": ["Nilgiri Peak", "Nilgiri Bandarban"],
                "media": [
                    {"media_type": "photo", "url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb", "caption": "Nilgiri peak surrounded by sea of clouds"}
                ],
                "reviews": [
                    {
                        "user": traveler_user1,
                        "rating": 5,
                        "visited_on": date(2025, 11, 20),
                        "travel_style": "comfort",
                        "group_type": "Family",
                        "group_size": 4,
                        "starting_location": "Chattogram",
                        "actual_cost_bdt": 6500.0,
                        "travel_guide": "The drive from Bandarban town to Nilgiri is breathtaking. Road quality is great. We stopped at Chimbuk Hill and Shailopropat waterfall on the way back.",
                        "crowd_level": "Moderate",
                        "access_difficulty": "Easy",
                        "road_condition": "Paved",
                        "pm_methods": ["Cash", "Card"],
                        "mobile_carrier": "GP",
                        "strongest_network": "4G",
                        "network_reliability": "Stable",
                        "safety": "Very safe",
                        "cleanliness": "Clean",
                    }
                ]
            },
            {
                "slug": "tanguar-haor-wetland",
                "name": "Tanguar Haor",
                "normalized_name": "tanguar-haor",
                "category": "Wetland & Lake",
                "summary": "A vast freshwater wetland RAMSAR site in Sunamganj famous for premium houseboat cruises.",
                "description": "Tanguar Haor is a RAMSAR wetland site spanning Sunamganj. It offers serene houseboat cruises, bird watching in winter, and crystal clear water under full moon skies.",
                "village": "Tahirpur",
                "upazila": "Tahirpur",
                "district": "Sunamganj",
                "division": "Sylhet",
                "nearest_hub": "Sunamganj Bus Stand",
                "latitude": 25.1534,
                "longitude": 91.0888,
                "best_season": "Monsoon (Jul-Oct) for water & Winter (Nov-Feb) for migratory birds",
                "suggested_duration": "2 days / 1 night",
                "guide_requirement": "Boat captain provided",
                "budget_min_bdt": 4000.0,
                "budget_max_bdt": 7000.0,
                "highlights": [
                    "Overnight luxury houseboat cruise",
                    "Niladri Lake (Tekerhat Limestone Lake)",
                    "Barikka Tila overlooking Meghalaya hills",
                    "Jadukata River crystal clear water"
                ],
                "know_before_you_go": [
                    "Book houseboats early for monsoon weekends.",
                    "Always wear life jackets while swimming in haor or Niladri lake.",
                    "Mobile network can drop in middle of haor."
                ],
                "tags": ["Haor", "Houseboat", "Wetland", "Sylhet"],
                "aliases": ["Tanguar Haor Sunamganj", "Niladri Lake"],
                "media": [
                    {"media_type": "photo", "url": "https://images.unsplash.com/photo-1544551763-46a013bb70d5", "caption": "Houseboat anchored on clear blue Tanguar Haor water"}
                ],
                "reviews": [
                    {
                        "user": traveler_user2,
                        "rating": 5,
                        "visited_on": date(2025, 8, 15),
                        "travel_style": "comfort",
                        "group_type": "Friends",
                        "group_size": 8,
                        "starting_location": "Dhaka",
                        "actual_cost_bdt": 5200.0,
                        "travel_guide": "We rented a premium houseboat from Tahirpur ghat. Includes 5 meals with fresh duck and haor fish. The evening full moon on water was unforgettable!",
                        "crowd_level": "Light crowd",
                        "access_difficulty": "Easy",
                        "road_condition": "Boat and walking",
                        "pm_methods": ["Cash", "bKash"],
                        "mobile_carrier": "GP",
                        "strongest_network": "3G",
                        "network_reliability": "Intermittent",
                        "safety": "Very safe",
                        "cleanliness": "Clean",
                    }
                ]
            },
            {
                "slug": "coxs-bazar-longest-sea-beach",
                "name": "Cox's Bazar Sea Beach",
                "normalized_name": "coxs-bazar-sea-beach",
                "category": "Beach & Island",
                "summary": "The world's longest unbroken natural sandy sea beach extending 120 km along the Bay of Bengal.",
                "description": "Cox's Bazar Beach is renowned for its smooth sandy slopes and sunsets over the ocean. It features Marine Drive, Himchari waterfalls, and Inani coral stone beach.",
                "village": "Kolatoli",
                "upazila": "Cox's Bazar Sadar",
                "district": "Cox's Bazar",
                "division": "Chattogram",
                "nearest_hub": "Kolatoli Dolphin Circle",
                "latitude": 21.4272,
                "longitude": 91.9702,
                "best_season": "October–April",
                "suggested_duration": "3 days / 2 nights",
                "guide_requirement": "Not required",
                "budget_min_bdt": 3500.0,
                "budget_max_bdt": 12000.0,
                "highlights": [
                    "World's longest unbroken 120km sandy beach",
                    "Scenic Marine Drive road trip to Teknaf",
                    "Inani golden coral beach",
                    "Fresh seafood at Kolatoli & Laboni beach"
                ],
                "know_before_you_go": [
                    "Follow lifeguard warnings and red flag indicators before swimming.",
                    "Negotiate beach quad bike and jet ski rides beforehand."
                ],
                "tags": ["Sea Beach", "Sunset", "Ocean", "Marine Drive"],
                "aliases": ["Cox Bazar", "Kolatoli Beach", "Inani Beach"],
                "media": [
                    {"media_type": "photo", "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e", "caption": "Sunset horizon at Laboni sea beach"}
                ],
                "reviews": [
                    {
                        "user": traveler_user3,
                        "rating": 4,
                        "visited_on": date(2025, 12, 25),
                        "travel_style": "comfort",
                        "group_type": "Family",
                        "group_size": 4,
                        "starting_location": "Dhaka",
                        "actual_cost_bdt": 6800.0,
                        "travel_guide": "Renting an open jeep on Marine Drive up to Teknaf is the best experience. Sunset at Inani beach is quieter than Kolatoli.",
                        "crowd_level": "Very crowded",
                        "access_difficulty": "Easy",
                        "road_condition": "Paved",
                        "pm_methods": ["Cash", "Card", "bKash"],
                        "mobile_carrier": "GP",
                        "strongest_network": "5G",
                        "network_reliability": "Stable",
                        "safety": "Very safe",
                        "cleanliness": "Okay",
                    }
                ]
            },
            {
                "slug": "sundarbans-mangrove-forest",
                "name": "Sundarbans Mangrove Forest",
                "normalized_name": "sundarbans-mangrove-forest",
                "category": "Wildlife & forest",
                "summary": "The largest contiguous mangrove forest in the world, home to the Royal Bengal Tiger and saltwater crocodiles.",
                "description": "The Sundarbans is a UNESCO World Heritage site located in southwestern Bangladesh. Cruising through narrow forest canals reveals spotted deer, wild boars, dolphins, and rich bird species.",
                "village": "Mongla",
                "upazila": "Mongla",
                "district": "Bagerhat",
                "division": "Khulna",
                "nearest_hub": "Mongla Port",
                "latitude": 21.9497,
                "longitude": 89.1833,
                "best_season": "November–March",
                "suggested_duration": "3 days / 2 nights",
                "guide_requirement": "Forest guard & licensed tour guide mandatory",
                "budget_min_bdt": 8500.0,
                "budget_max_bdt": 16000.0,
                "highlights": [
                    "Katamka & Dublar Char wildlife trails",
                    "Harbaria Eco-tourism center wooden boardwalk",
                    "Early morning quiet canal boat silent paddling",
                    "Royal Bengal tiger footprint tracking"
                ],
                "know_before_you_go": [
                    "3-day ship permits are issued via forest department registered tour operators.",
                    "Armed forest guards accompany all walking expeditions.",
                    "No mobile network coverage in deep forest zones."
                ],
                "tags": ["UNESCO", "Mangrove", "Tiger", "Wildlife"],
                "aliases": ["Sundarbans Mongla", "Katamka Forest"],
                "media": [
                    {"media_type": "photo", "url": "https://images.unsplash.com/photo-1516426122078-c23e76319801", "caption": "Sundarbans river channel and dense mangrove canopy"}
                ],
                "reviews": [
                    {
                        "user": traveler_user1,
                        "rating": 5,
                        "visited_on": date(2026, 1, 10),
                        "travel_style": "adventure",
                        "group_type": "Friends",
                        "group_size": 6,
                        "starting_location": "Khulna",
                        "actual_cost_bdt": 12500.0,
                        "travel_guide": "We boarded a tourist vessel from Mongla. Seeing spotted deer drinking at Katamka beach and listening to forest birds in early morning silence was magical!",
                        "crowd_level": "Quiet",
                        "access_difficulty": "Moderate",
                        "road_condition": "Boat and walking",
                        "pm_methods": ["Cash"],
                        "mobile_carrier": "Teletalk",
                        "strongest_network": "No signal",
                        "network_reliability": "Unreliable",
                        "safety": "Very safe",
                        "cleanliness": "Clean",
                    }
                ]
            }
        ]

        for pdata in places_data:
            existing = db.query(Place).filter(Place.slug == pdata["slug"]).first()
            if existing:
                continue

            tags_list = pdata.pop("tags")
            aliases_list = pdata.pop("aliases")
            media_list = pdata.pop("media")
            reviews_list = pdata.pop("reviews")

            place = Place(
                id=uuid.uuid4(),
                status="approved",
                approved_by=admin_user.id,
                approved_at=datetime.now(timezone.utc),
                **pdata,
            )
            db.add(place)
            db.flush()

            for t in tags_list:
                db.add(PlaceTag(place_id=place.id, tag=t))

            for a in aliases_list:
                db.add(PlaceAlias(place_id=place.id, alias=a, normalized_alias=a.lower().replace(" ", "-")))

            for idx, m in enumerate(media_list):
                db.add(
                    PlaceMedia(
                        place_id=place.id,
                        uploaded_by=admin_user.id,
                        media_type=m["media_type"],
                        url=m["url"],
                        caption=m.get("caption"),
                        platform=m.get("platform"),
                        sort_order=idx,
                    )
                )

            for r in reviews_list:
                rev_user = r.pop("user")
                pm_list = r.pop("pm_methods")
                rev = Review(
                    id=uuid.uuid4(),
                    place_id=place.id,
                    user_id=rev_user.id,
                    status="published",
                    **r,
                )
                db.add(rev)
                db.flush()

                for pm in pm_list:
                    db.add(ReviewPaymentMethod(review_id=rev.id, payment_method=pm))

        # 3. Seed 6 Travel Buddy Trips
        trips_data = [
            {
                "title": "Cloudy Sajek weekend getaway",
                "creator": traveler_user1,
                "origin": "Dhaka",
                "destination": "Sajek Valley",
                "start_at": datetime(2026, 8, 28, 22, 30, tzinfo=timezone.utc),
                "end_at": datetime(2026, 8, 31, 6, 0, tzinfo=timezone.utc),
                "meeting_point": "Arambagh bus counter, Dhaka",
                "transport": "Night bus to Khagrachari, then reserved chander gari",
                "estimated_cost_min_bdt": 5500.0,
                "estimated_cost_max_bdt": 6500.0,
                "description": "A relaxed weekend for sunrise, short walks and local food. We will travel overnight so both full days remain free in Sajek.",
                "itinerary": "Friday night departure from Dhaka. Saturday: Khagrachari breakfast, Sajek check-in and sunset. Sunday: sunrise, Konglak walk and free time. Return Sunday evening.",
                "max_members": 8,
                "status": "published",
                "communication_platform": "WhatsApp",
                "communication_note": "The confirmed travelers receive the WhatsApp group invite by email.",
                "requirements": ["Carry photo ID", "Comfortable with shared rooms", "Pay transport advance"]
            },
            {
                "title": "Debotakhum river canyon journey",
                "creator": traveler_user2,
                "origin": "Chattogram",
                "destination": "Debotakhum",
                "start_at": datetime(2026, 9, 11, 5, 30, tzinfo=timezone.utc),
                "end_at": datetime(2026, 9, 13, 22, 0, tzinfo=timezone.utc),
                "meeting_point": "BRTC bus counter, Chattogram",
                "transport": "Local bus, reserved jeep, boat and short trek",
                "estimated_cost_min_bdt": 4200.0,
                "estimated_cost_max_bdt": 5200.0,
                "description": "A small-group adventure to Debotakhum with an early start, local guide and a night in Rowangchhari.",
                "itinerary": "Travel to Bandarban and Rowangchhari on day one. Visit Debotakhum with a local guide on day two. Return through Bandarban on day three.",
                "max_members": 6,
                "status": "published",
                "communication_platform": "Telegram",
                "communication_note": "A private Telegram group is shared after your place is confirmed.",
                "requirements": ["Able to walk on wet terrain", "Carry cash", "Follow local guide safety decisions"]
            },
            {
                "title": "Full-moon haor houseboat journey",
                "creator": traveler_user3,
                "origin": "Sylhet",
                "destination": "Tanguar Haor",
                "start_at": datetime(2026, 9, 25, 6, 0, tzinfo=timezone.utc),
                "end_at": datetime(2026, 9, 26, 20, 0, tzinfo=timezone.utc),
                "meeting_point": "Ambarkhana Point, Sylhet",
                "transport": "Reserved microbus to Tahirpur and overnight boat",
                "estimated_cost_min_bdt": 3800.0,
                "estimated_cost_max_bdt": 4500.0,
                "description": "An overnight boat journey focused on open water, village stops and a quiet full-moon evening.",
                "itinerary": "Morning departure for Tahirpur, board before lunch, overnight on the haor, return to Sylhet the following evening.",
                "max_members": 14,
                "status": "published",
                "communication_platform": "Messenger",
                "communication_note": "The organizer will email the Messenger group link after confirmation.",
                "requirements": ["Bring light blanket", "Shared sleeping deck", "Respect local villages"]
            },
            {
                "title": "Tea garden cycling escape",
                "creator": traveler_user1,
                "origin": "Dhaka",
                "destination": "Sreemangal",
                "start_at": datetime(2026, 10, 9, 6, 30, tzinfo=timezone.utc),
                "end_at": datetime(2026, 10, 10, 22, 30, tzinfo=timezone.utc),
                "meeting_point": "Kamalapur Railway Station",
                "transport": "Intercity train and rented bicycles",
                "estimated_cost_min_bdt": 3000.0,
                "estimated_cost_max_bdt": 4000.0,
                "description": "A beginner-friendly cycling weekend through tea gardens with plenty of rest stops.",
                "itinerary": "Train to Sreemangal, afternoon tea garden ride, morning cycle to Baikka Beel, return by evening train.",
                "max_members": 10,
                "status": "published",
                "communication_platform": "WhatsApp",
                "communication_note": "Coordination happens in WhatsApp once confirmed.",
                "requirements": ["Know basic cycling", "Refillable water bottle", "Helmet rental included"]
            },
            {
                "title": "Kuakata sunrise and sunset beach weekend",
                "creator": traveler_user2,
                "origin": "Barishal",
                "destination": "Kuakata",
                "start_at": datetime(2026, 10, 23, 7, 0, tzinfo=timezone.utc),
                "end_at": datetime(2026, 10, 24, 19, 0, tzinfo=timezone.utc),
                "meeting_point": "Nathullabad bus terminal",
                "transport": "Direct local bus and shared auto-rickshaw",
                "estimated_cost_min_bdt": 2800.0,
                "estimated_cost_max_bdt": 3600.0,
                "description": "A simple beach weekend with both sunrise and sunset, local food and no packed schedule.",
                "itinerary": "Saturday arrival and sunset; Sunday sunrise, beach exploration and evening return to Barishal.",
                "max_members": 6,
                "status": "published",
                "communication_platform": "Messenger",
                "communication_note": "Messenger group invite arrives with your confirmation email.",
                "requirements": ["Shared twin rooms", "Bring sun protection", "Respect agreed departure time"]
            },
            {
                "title": "Ratargul morning paddle & forest lunch",
                "creator": traveler_user3,
                "origin": "Sylhet",
                "destination": "Ratargul Swamp Forest",
                "start_at": datetime(2026, 11, 7, 6, 0, tzinfo=timezone.utc),
                "end_at": datetime(2026, 11, 7, 16, 0, tzinfo=timezone.utc),
                "meeting_point": "Shahjalal Uposhohor, Sylhet",
                "transport": "Reserved CNG and local wooden boats",
                "estimated_cost_min_bdt": 1400.0,
                "estimated_cost_max_bdt": 1900.0,
                "description": "A one-day early morning visit for calm water, photography and lunch near the forest.",
                "itinerary": "Meet at 6:00 AM, reach Ratargul before crowds, two-hour boat session, local lunch and return by 4:00 PM.",
                "max_members": 7,
                "status": "published",
                "communication_platform": "Telegram",
                "communication_note": "Confirmed travelers are invited to Telegram by email.",
                "requirements": ["Arrive on time", "Use life jacket", "Keep electronics waterproof"]
            }
        ]

        for tdata in trips_data:
            creator_usr = tdata.pop("creator")
            reqs = tdata.pop("requirements")

            existing_trip = db.query(TravelTrip).filter(TravelTrip.title == tdata["title"]).first()
            if existing_trip:
                continue

            trip = TravelTrip(
                id=uuid.uuid4(),
                creator_id=creator_usr.id,
                **tdata,
            )
            db.add(trip)
            db.flush()

            # Creator as member with host role
            db.add(
                TravelTripMember(
                    trip_id=trip.id,
                    user_id=creator_usr.id,
                    role="host",
                    status="accepted",
                )
            )

            for idx, req_str in enumerate(reqs):
                db.add(
                    TravelTripRequirement(
                        trip_id=trip.id,
                        requirement=req_str,
                        sort_order=idx,
                    )
                )

        db.commit()
        logger.info("Successfully seeded database with 6 rich Bangladesh places and 6 public travel trips!")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
