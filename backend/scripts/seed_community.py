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
from app.models.entry_video_embed import EntryVideoEmbed

def seed():
    db = SessionLocal()
    try:
        # 1. Get the existing user
        user = db.query(User).first()
        if not user:
            print("No users found. Please login once via the frontend to create a user.")
            return
        
        user_id = user.id
        print(f"Seeding data for user: {user.name} ({user_id})")

        # 2. Clear existing entries to avoid duplicates if run multiple times
        db.query(EntryPhoto).delete()
        db.query(EntryVideoEmbed).delete()
        db.query(CommunityEntry).delete()
        db.commit()

        # 3. Sample Entries
        entries_data = [
            {
                "name": "Sajek Valley",
                "category": "attraction",
                "location": "Baghaichhari, Rangamati",
                "price_range": "mid_range",
                "tags": ["trending", "hidden_gem"],
                "amenities": ["Cloud View", "Local Food", "Hiking", "Resorts"],
                "travel_tips": "Best time to visit is from October to February. Carry a power bank and enough cash as there are no ATMs.",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1623059859556-97274094a973?q=80&w=1000", "public_id": "seed/sajek_1", "caption": "Morning clouds over Sajek"},
                    {"url": "https://images.unsplash.com/photo-1583000962354-954003d15732?q=80&w=1000", "public_id": "seed/sajek_2", "caption": "Wooden cottage in Sajek"}
                ],
                "videos": [
                    {"url": "https://www.youtube.com/watch?v=07d2dXHYb94", "platform": "youtube"}
                ]
            },
            {
                "name": "Panigram Resort",
                "category": "hotel",
                "location": "Jessore",
                "price_range": "premium",
                "tags": ["hidden_gem"],
                "amenities": ["Spa", "Organic Food", "Swimming Pool", "Bicycle Rental"],
                "travel_tips": "A sustainable boutique resort. Great for a quiet weekend getaway.",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1000", "public_id": "seed/panigram_1", "caption": "Resort Entrance"}
                ],
                "videos": []
            },
            {
                "name": "Ratargul Swamp Forest",
                "category": "attraction",
                "location": "Sylhet",
                "price_range": "budget",
                "tags": ["trending"],
                "amenities": ["Boat Trip", "Wildlife", "Photography"],
                "travel_tips": "Hire a boat from the local stand. Best seen during monsoon (June to September).",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1590603740183-980e7f6920eb?q=80&w=1000", "public_id": "seed/ratargul_1", "caption": "Boating in the swamp forest"}
                ],
                "videos": [
                    {"url": "https://www.youtube.com/watch?v=kYv_w2lM_w4", "platform": "youtube"}
                ]
            },
            {
                "name": "Puran Dhaka Kitchen",
                "category": "restaurant",
                "location": "Old Dhaka",
                "price_range": "budget",
                "tags": ["trending"],
                "amenities": ["Kacchi Biryani", "Authentic Spices", "Takeaway"],
                "travel_tips": "Must try their Mutton Kacchi. The place is small and crowded but the food is legendary.",
                "photos": [
                    {"url": "https://images.unsplash.com/photo-1589187151032-573a91317445?q=80&w=1000", "public_id": "seed/biryani_1", "caption": "Authentic Biryani"}
                ],
                "videos": []
            }
        ]

        for data in entries_data:
            photos_data = data.pop("photos")
            videos_data = data.pop("videos")
            
            entry = CommunityEntry(**data, user_id=user_id)
            db.add(entry)
            db.flush() # Get entry.id

            for p in photos_data:
                db.add(EntryPhoto(**p, entry_id=entry.id))
            
            for v in videos_data:
                db.add(EntryVideoEmbed(**v, entry_id=entry.id))

        db.commit()
        print(f"Successfully seeded {len(entries_data)} community entries!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
