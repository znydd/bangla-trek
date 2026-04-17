#!/usr/bin/env python3
"""
Seed test itineraries for Buddy Matching feature.
Creates multiple users with overlapping destinations/interests.
No AI required - data is hardcoded for consistent testing.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.itinerary import Itinerary, ItineraryActivity


def seed_test_data():
    db = SessionLocal()
    try:
        # Get or create test users
        users = db.query(User).all()
        if len(users) < 2:
            print("Need at least 2 users. Please login with 2 different Google accounts first.")
            return

        print(f"Found {len(users)} users. Seeding itineraries...")

        # Clear existing itineraries
        db.query(ItineraryActivity).delete()
        db.query(Itinerary).delete()
        db.commit()

        # Test data: overlapping destinations and interests
        test_itineraries = [
            # User 1: Sylhet trip with nature/photography interests
            {
                "user_index": 0,
                "destination": "Sylhet",
                "duration_days": 3,
                "budget": 15000,
                "travel_style": "comfort",
                "interests": ["nature", "photography", "tea gardens", "waterfalls"],
                "group_type": "friends",
                "activities": [
                    {"day": 1, "start": "08:00", "end": "10:00", "title": "Visit Ratargul Swamp Forest", "cost": 500},
                    {"day": 1, "start": "14:00", "end": "17:00", "title": "Tea Garden Photography", "cost": 200},
                    {"day": 2, "start": "09:00", "end": "12:00", "title": "Jaflong Stone Collection", "cost": 800},
                    {"day": 2, "start": "15:00", "end": "17:00", "title": "Lalakhal Boat Ride", "cost": 1000},
                    {"day": 3, "start": "06:00", "end": "09:00", "title": "Sunrise at Bichanakandi", "cost": 600},
                ]
            },
            # User 2: Sylhet trip with similar interests (high match potential)
            {
                "user_index": 1,
                "destination": "Sylhet",
                "duration_days": 4,
                "budget": 20000,
                "travel_style": "comfort",
                "interests": ["nature", "photography", "hiking", "tea gardens"],
                "group_type": "solo",
                "activities": [
                    {"day": 1, "start": "10:00", "end": "13:00", "title": "Madhabkunda Waterfall", "cost": 1200},
                    {"day": 2, "start": "08:00", "end": "11:00", "title": "Ratargul Boat Tour", "cost": 600},
                    {"day": 2, "start": "14:00", "end": "16:00", "title": "Srimangal Tea Estate", "cost": 300},
                    {"day": 3, "start": "09:00", "end": "12:00", "title": "Lawachara Forest Trek", "cost": 800},
                    {"day": 4, "start": "05:00", "end": "08:00", "title": "Dawn Photography at Tea Gardens", "cost": 200},
                ]
            },
            # User 1: Cox's Bazar (different destination - lower match)
            {
                "user_index": 0,
                "destination": "Cox's Bazar",
                "duration_days": 2,
                "budget": 12000,
                "travel_style": "budget",
                "interests": ["beaches", "seafood", "sunset"],
                "group_type": "couple",
                "activities": [
                    {"day": 1, "start": "16:00", "end": "18:00", "title": "Sunset at Laboni Beach", "cost": 0},
                    {"day": 1, "start": "19:00", "end": "21:00", "title": "Seafood Dinner", "cost": 1500},
                    {"day": 2, "start": "10:00", "end": "14:00", "title": "Inani Beach Visit", "cost": 800},
                ]
            },
        ]

        count = 0
        for data in test_itineraries:
            user = users[data["user_index"]]
            
            itinerary = Itinerary(
                user_id=user.id,
                destination=data["destination"],
                duration_days=data["duration_days"],
                budget=data["budget"],
                travel_style=data["travel_style"],
                interests=data["interests"],
                group_type=data["group_type"],
            )
            db.add(itinerary)
            db.flush()  # Get itinerary.id

            for act in data["activities"]:
                activity = ItineraryActivity(
                    itinerary_id=itinerary.id,
                    day_number=act["day"],
                    start_time=act["start"],
                    end_time=act["end"],
                    title=act["title"],
                    description=f"Activity on day {act['day']}: {act['title']}",
                    estimated_cost=act["cost"],
                    location=data["destination"],
                    category="sightseeing",
                )
                db.add(activity)

            count += 1
            print(f"  Created itinerary #{count}: {data['destination']} for {user.name}")

        db.commit()
        print(f"\n✅ Successfully seeded {count} test itineraries!")
        print("\nNow go to /buddy-matching to see the matches.")
        print("Expected: User 1 and User 2 should have high match scores for Sylhet.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed_test_data()
