#!/usr/bin/env python3
"""
Seed detailed entry reviews and review photos.

This script populates:
- entry_reviews
- entry_review_photos

Run after community/accommodation/itinerary seed scripts.
"""

import os
import sys

# Add backend directory to sys.path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.community_entry import CommunityEntry
from app.models.entry_review import EntryReview
from app.models.entry_review_photo import EntryReviewPhoto
from app.models.itinerary import ItineraryActivity
from app.models.user import User


def seed_reviews():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if len(users) < 2:
            print("Need at least 2 users. Please create/login users first.")
            return

        entries = db.query(CommunityEntry).all()
        if not entries:
            print("No community entries found. Run community/accommodation seeding first.")
            return

        print(f"Found {len(users)} users and {len(entries)} entries.")

        # Clear existing review seed data to keep runs idempotent
        db.query(EntryReviewPhoto).delete()
        db.query(EntryReview).delete()
        db.commit()

        # Map entry -> itinerary activity when available for optional linkage
        activity_by_entry = {}
        activities = (
            db.query(ItineraryActivity)
            .filter(ItineraryActivity.community_entry_id.isnot(None))
            .all()
        )
        for activity in activities:
            entry_id = activity.community_entry_id
            if entry_id and entry_id not in activity_by_entry:
                activity_by_entry[entry_id] = activity

        # Choose entries with useful categories first, then fall back to any
        preferred_categories = {"attraction", "hotel", "guesthouse", "homestay", "restaurant"}
        selected_entries = [e for e in entries if e.category in preferred_categories]
        if len(selected_entries) < 6:
            selected_entries = entries

        review_templates = [
            {
                "rating": 5,
                "travel_style": "budget",
                "actual_cost_bdt": 1200,
                "time_spent_minutes": 180,
                "review_text": "Great value for money. We spent most of the morning here and the local food stalls were very affordable. Arrive early to avoid crowds.",
                "photos": [
                    {
                        "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1000",
                        "public_id": "seed/reviews/review_1_1",
                        "caption": "Morning view",
                    }
                ],
            },
            {
                "rating": 4,
                "travel_style": "family",
                "actual_cost_bdt": 2800,
                "time_spent_minutes": 210,
                "review_text": "Family friendly and easy to navigate with kids. Clean environment and plenty of shaded resting spots. Weekdays are much better than weekends.",
                "photos": [
                    {
                        "url": "https://images.unsplash.com/photo-1472396961693-142e6e269027?q=80&w=1000",
                        "public_id": "seed/reviews/review_2_1",
                        "caption": "Wide open area",
                    }
                ],
            },
            {
                "rating": 5,
                "travel_style": "adventure",
                "actual_cost_bdt": 4500,
                "time_spent_minutes": 300,
                "review_text": "Perfect for adventure style travel. Trails were exciting and the guide knew alternative routes. Bring water, sunscreen, and shoes with good grip.",
                "photos": [],
            },
            {
                "rating": 3,
                "travel_style": "luxury",
                "actual_cost_bdt": 8500,
                "time_spent_minutes": 160,
                "review_text": "Comfortable stay and decent service, but premium pricing felt a bit high for what we got. Location is excellent, so convenience balances it out.",
                "photos": [
                    {
                        "url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1000",
                        "public_id": "seed/reviews/review_4_1",
                        "caption": "Hotel exterior",
                    }
                ],
            },
            {
                "rating": 4,
                "travel_style": "budget",
                "actual_cost_bdt": 950,
                "time_spent_minutes": 120,
                "review_text": "A solid budget option with clean rooms and helpful staff. Not fancy, but practical if your plan is to spend more time outside exploring.",
                "photos": [],
            },
            {
                "rating": 5,
                "travel_style": "family",
                "actual_cost_bdt": 3200,
                "time_spent_minutes": 240,
                "review_text": "Excellent for family trips. We had safe transport options nearby and food choices for different age groups. Staff were very supportive.",
                "photos": [
                    {
                        "url": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?q=80&w=1000",
                        "public_id": "seed/reviews/review_6_1",
                        "caption": "Relaxed evening",
                    }
                ],
            },
            {
                "rating": 4,
                "travel_style": "adventure",
                "actual_cost_bdt": 2100,
                "time_spent_minutes": 195,
                "review_text": "Good base for nearby hikes and local experiences. Connectivity can be patchy at times, so keep offline maps downloaded before you start.",
                "photos": [],
            },
            {
                "rating": 5,
                "travel_style": "luxury",
                "actual_cost_bdt": 12000,
                "time_spent_minutes": 220,
                "review_text": "Premium experience with excellent ambience and polished service. The location made daily movement easy and saved time on transport.",
                "photos": [
                    {
                        "url": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?q=80&w=1000",
                        "public_id": "seed/reviews/review_8_1",
                        "caption": "Lobby and interior",
                    }
                ],
            },
        ]

        created = 0
        used_pairs = set()

        for idx, template in enumerate(review_templates):
            entry = selected_entries[idx % len(selected_entries)]
            user = users[idx % len(users)]

            # Respect unique(entry_id, user_id) constraint
            pair = (str(entry.id), str(user.id))
            if pair in used_pairs:
                continue
            used_pairs.add(pair)

            review = EntryReview(
                entry_id=entry.id,
                user_id=user.id,
                rating=template["rating"],
                travel_style=template["travel_style"],
                actual_cost_bdt=template["actual_cost_bdt"],
                time_spent_minutes=template["time_spent_minutes"],
                review_text=template["review_text"],
            )

            matched_activity = activity_by_entry.get(entry.id)
            if matched_activity:
                review.activity_id = matched_activity.id
                review.itinerary_id = matched_activity.itinerary_id

            db.add(review)
            db.flush()  # get review.id

            for photo in template["photos"]:
                db.add(
                    EntryReviewPhoto(
                        review_id=review.id,
                        url=photo["url"],
                        public_id=photo["public_id"],
                        caption=photo["caption"],
                    )
                )

            created += 1
            print(f"  Added review #{created} for '{entry.name}' by {user.name}")

        db.commit()
        print(f"\nSuccessfully seeded {created} detailed reviews.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding reviews: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed_reviews()
