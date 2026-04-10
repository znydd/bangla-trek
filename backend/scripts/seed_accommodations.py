import uuid
import sys
import os

# Add the backend directory to sys.path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.community_entry import CommunityEntry
from app.models.entry_photo import EntryPhoto


def seed():
    db = SessionLocal()
    try:
        # 1. Get the existing user
        user = db.query(User).first()
        if not user:
            print("No users found. Please login once via the frontend to create a user.")
            return

        user_id = user.id
        print(f"Seeding accommodations for user: {user.name} ({user_id})")

        # 2. Remove only accommodation-type entries (hotel, guesthouse, homestay)
        accommodation_categories = ["hotel", "guesthouse", "homestay"]
        existing_ids = [
            row[0]
            for row in db.query(CommunityEntry.id)
            .filter(CommunityEntry.category.in_(accommodation_categories))
            .all()
        ]
        if existing_ids:
            db.query(EntryPhoto).filter(EntryPhoto.entry_id.in_(existing_ids)).delete(
                synchronize_session=False
            )
            db.query(CommunityEntry).filter(CommunityEntry.id.in_(existing_ids)).delete(
                synchronize_session=False
            )
            db.commit()
            print(f"Cleared {len(existing_ids)} old accommodation entries.")

        # 3. Accommodation seed data
        entries_data = [
            # ═══════════════════════════════════════
            # Cox's Bazar
            # ═══════════════════════════════════════
            {
                "name": "Hotel Sea Crown",
                "category": "hotel",
                "location": "Kalatali Road, Cox's Bazar",
                "latitude": 21.4272,
                "longitude": 91.9710,
                "price_range": "mid_range",
                "tags": ["trending"],
                "amenities": ["WiFi", "AC", "Room Service", "Sea View", "Restaurant"],
                "travel_tips": "Ask for a room on the 5th floor or above for the best sea views. Walking distance to Kalatali Beach. Book ahead during Eid holidays.",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1000", "public_id": "seed/acc_seacrown_1", "caption": "Hotel Sea Crown exterior"},
                ],
            },
            {
                "name": "Long Beach Hotel",
                "category": "hotel",
                "location": "Kolatoli, Cox's Bazar",
                "latitude": 21.4285,
                "longitude": 91.9722,
                "price_range": "premium",
                "tags": ["trending"],
                "amenities": ["WiFi", "AC", "Swimming Pool", "Gym", "Spa", "Restaurant", "Sea View"],
                "travel_tips": "One of the most well-known hotels in Cox's Bazar. Their rooftop restaurant has an incredible sunset view. Try to book the deluxe sea-facing rooms.",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1564501049412-61c2a3083791?q=80&w=1000", "public_id": "seed/acc_longbeach_1", "caption": "Poolside at Long Beach Hotel"},
                ],
            },
            {
                "name": "Nazmul's Beach Homestay",
                "category": "homestay",
                "location": "Laboni Point, Cox's Bazar",
                "latitude": 21.4317,
                "longitude": 91.9758,
                "price_range": "budget",
                "tags": ["hidden_gem"],
                "amenities": ["Fan", "Home-cooked Meals", "Local Guide"],
                "travel_tips": "A cozy family-run homestay just 3 mins from Laboni Beach. Nazmul bhai can arrange fishing trips. No AC but sea breeze keeps it cool at night.",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1587061949409-02df41d5e562?q=80&w=1000", "public_id": "seed/acc_nazmul_1", "caption": "Cozy homestay room"},
                ],
            },
            {
                "name": "Mermaid Beach Resort",
                "category": "hotel",
                "location": "Inani Beach, Cox's Bazar",
                "latitude": 21.3456,
                "longitude": 92.0123,
                "price_range": "luxury",
                "tags": ["trending"],
                "amenities": ["WiFi", "AC", "Private Beach", "Swimming Pool", "Spa", "Restaurant", "Bar"],
                "travel_tips": "Located right on Inani Beach, one of the most beautiful stretches in Bangladesh. Worth the extra distance from the city center. Pre-book airport transfers.",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?q=80&w=1000", "public_id": "seed/acc_mermaid_1", "caption": "Beachfront resort view"},
                ],
            },
            {
                "name": "Hillside Guest House",
                "category": "guesthouse",
                "location": "Himchori Road, Cox's Bazar",
                "latitude": 21.3890,
                "longitude": 91.9945,
                "price_range": "budget",
                "tags": [],
                "amenities": ["Fan", "Hot Water", "Parking", "Garden"],
                "travel_tips": "A quiet guesthouse away from the crowded Kalatoli strip. Good for families who want peace and quiet. The caretaker speaks basic English.",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1582719508461-905c673771fd?q=80&w=1000", "public_id": "seed/acc_hillside_1", "caption": "Hillside Guest House garden"},
                ],
            },
            # ═══════════════════════════════════════
            # Sylhet
            # ═══════════════════════════════════════
            {
                "name": "Grand Sultan Tea Resort",
                "category": "hotel",
                "location": "Srimangal, Sylhet",
                "latitude": 24.3065,
                "longitude": 91.7296,
                "price_range": "premium",
                "tags": ["trending"],
                "amenities": ["WiFi", "AC", "Swimming Pool", "Tea Garden Tour", "Restaurant", "Spa"],
                "travel_tips": "Surrounded by lush tea gardens. Their guided tea-tasting experience is a must. Book the garden-view bungalows for the best atmosphere.",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?q=80&w=1000", "public_id": "seed/acc_sultan_1", "caption": "Resort nestled in tea gardens"},
                ],
            },
            {
                "name": "Nazimgarh Wilderness Resort",
                "category": "hotel",
                "location": "Nazimgarh, Sylhet",
                "latitude": 24.8853,
                "longitude": 91.8753,
                "price_range": "premium",
                "tags": ["hidden_gem"],
                "amenities": ["WiFi", "AC", "Restaurant", "Hiking Trails", "Lake View", "Bonfire"],
                "travel_tips": "One of the most scenic resorts in Bangladesh. Built on a hillside overlooking a lake. The zipline and kayaking activities are a must-try.",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?q=80&w=1000", "public_id": "seed/acc_nazim_1", "caption": "Lake view from balcony"},
                ],
            },
            {
                "name": "Rema Homestay",
                "category": "homestay",
                "location": "Rema-Kalenga, Habiganj, Sylhet",
                "latitude": 24.1139,
                "longitude": 91.6361,
                "price_range": "budget",
                "tags": ["hidden_gem"],
                "amenities": ["Home-cooked Meals", "Forest Guide", "Birdwatching"],
                "travel_tips": "Stay with a Khasi tribal family near Rema-Kalenga Wildlife Sanctuary. Incredible birdwatching at dawn. Carry mosquito repellent and a flashlight.",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1510798831971-661eb04b3739?q=80&w=1000", "public_id": "seed/acc_rema_1", "caption": "Rustic forest homestay"},
                ],
            },
            # ═══════════════════════════════════════
            # Bandarban
            # ═══════════════════════════════════════
            {
                "name": "Nilgiri Hills Resort",
                "category": "hotel",
                "location": "Nilgiri, Bandarban",
                "latitude": 21.7830,
                "longitude": 92.3710,
                "price_range": "mid_range",
                "tags": ["trending"],
                "amenities": ["Restaurant", "Cloud View", "Parking", "Generator"],
                "travel_tips": "At 2000+ ft, Nilgiri is often above the clouds. Military-run resort so it's very safe. Book through the Bandarban army cantonment office.",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1596178065887-1198b6148b2b?q=80&w=1000", "public_id": "seed/acc_nilgiri_1", "caption": "Clouds below the resort"},
                ],
            },
            {
                "name": "Hillside Resort Bandarban",
                "category": "hotel",
                "location": "Bandarban Town",
                "latitude": 22.1953,
                "longitude": 92.2184,
                "price_range": "mid_range",
                "tags": [],
                "amenities": ["WiFi", "AC", "Restaurant", "Mountain View", "Parking"],
                "travel_tips": "Located at the heart of Bandarban town. Great base for day trips to Nilachal, Golden Temple, and Boga Lake. Can arrange jeep hire.",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1445019980597-93fa8acb246c?q=80&w=1000", "public_id": "seed/acc_hillresort_1", "caption": "Mountain view room"},
                ],
            },
            {
                "name": "Marma Tribal Homestay",
                "category": "homestay",
                "location": "Ruma, Bandarban",
                "latitude": 21.9816,
                "longitude": 92.3975,
                "price_range": "budget",
                "tags": ["hidden_gem"],
                "amenities": ["Traditional Meals", "Cultural Experience", "Trekking Guide"],
                "travel_tips": "An authentic experience with a Marma family. They can guide you on the 3-day Boga Lake trek. Bring your own sleeping bag for extra comfort.",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?q=80&w=1000", "public_id": "seed/acc_marma_1", "caption": "Traditional bamboo house"},
                ],
            },
            # ═══════════════════════════════════════
            # Sundarbans
            # ═══════════════════════════════════════
            {
                "name": "Sundarbans Tiger Camp",
                "category": "guesthouse",
                "location": "Khulna, Sundarbans Gateway",
                "latitude": 22.3216,
                "longitude": 89.1500,
                "price_range": "mid_range",
                "tags": ["trending"],
                "amenities": ["Boat Tour", "Nature Guide", "Meals Included", "Generator"],
                "travel_tips": "A popular base camp for Sundarbans boat tours. They offer 2-day and 3-day packages including forest permits, meals, and boat hire. Book at least a week ahead.",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?q=80&w=1000", "public_id": "seed/acc_tigercamp_1", "caption": "Riverside camp at dusk"},
                ],
            },
            # ═══════════════════════════════════════
            # Rangamati
            # ═══════════════════════════════════════
            {
                "name": "Parjatan Motel Rangamati",
                "category": "hotel",
                "location": "Deer Park, Rangamati",
                "latitude": 22.6372,
                "longitude": 92.2054,
                "price_range": "mid_range",
                "tags": [],
                "amenities": ["AC", "Lake View", "Restaurant", "Parking", "Garden"],
                "travel_tips": "Government-run motel right on Kaptai Lake. The lakeside rooms are stunning at sunset. It fills up fast during public holidays so book early.",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?q=80&w=1000", "public_id": "seed/acc_parjatan_1", "caption": "View of Kaptai Lake"},
                ],
            },
            {
                "name": "Chakma Heritage Homestay",
                "category": "homestay",
                "location": "Rangamati Sadar",
                "latitude": 22.6320,
                "longitude": 92.1980,
                "price_range": "budget",
                "tags": ["hidden_gem"],
                "amenities": ["Traditional Meals", "Cultural Immersion", "Boat Ride"],
                "travel_tips": "Stay with a Chakma family and experience indigenous culture firsthand. They prepare amazing traditional bamboo-cooked dishes. Very welcoming hosts.",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1540541338287-41700207dee6?q=80&w=1000", "public_id": "seed/acc_chakma_1", "caption": "Lake-side traditional home"},
                ],
            },
            # ═══════════════════════════════════════
            # Dhaka
            # ═══════════════════════════════════════
            {
                "name": "Pan Pacific Sonargaon Dhaka",
                "category": "hotel",
                "location": "Karwan Bazar, Dhaka",
                "latitude": 23.7512,
                "longitude": 90.3930,
                "price_range": "luxury",
                "tags": [],
                "amenities": ["WiFi", "AC", "Swimming Pool", "Gym", "Spa", "Restaurant", "Bar", "Business Center"],
                "travel_tips": "One of the iconic 5-star hotels in Dhaka. Centrally located near major business hubs. Their Sunday brunch buffet is legendary among locals.",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?q=80&w=1000", "public_id": "seed/acc_sonargaon_1", "caption": "Luxury hotel lobby"},
                ],
            },
            {
                "name": "Hotel 71",
                "category": "hotel",
                "location": "Mohakhali, Dhaka",
                "latitude": 23.7780,
                "longitude": 90.4020,
                "price_range": "mid_range",
                "tags": [],
                "amenities": ["WiFi", "AC", "Restaurant", "Parking", "Room Service"],
                "travel_tips": "A solid mid-range option in Dhaka. Clean rooms, reliable WiFi. Close to Hatirjheel lakefront for evening walks. Good value for money.",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1618773928121-c32242e63f39?q=80&w=1000", "public_id": "seed/acc_hotel71_1", "caption": "Clean modern room"},
                ],
            },
        ]

        count = 0
        for data in entries_data:
            photos_data = data.pop("photos")

            entry = CommunityEntry(**data, user_id=user_id)
            db.add(entry)
            db.flush()  # Get entry.id

            for p in photos_data:
                db.add(EntryPhoto(**p, entry_id=entry.id))

            count += 1

        db.commit()
        print(f"Successfully seeded {count} accommodation entries!")
        print("Locations covered: Cox's Bazar, Sylhet, Bandarban, Sundarbans, Rangamati, Dhaka")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
