import uuid
import os
import sys
from datetime import datetime, date, timedelta

# Add the backend directory to sys.path so this script works when run directly.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.community_entry import CommunityEntry
from app.models.nomad_metrics import NomadMetric
from app.models.transit_blueprint import TransitBlueprint
from app.models.emergency_facility import EmergencyFacility
from app.models.itinerary import Itinerary, ItineraryActivity

def seed_demo_data():
    db = SessionLocal()
    try:
        # 1. Create/Get Demo User
        demo_user = db.query(User).filter(User.email == "demo@banglatrek.com").first()
        if not demo_user:
            demo_user = User(
                google_id="demo-user-123456",
                email="demo@banglatrek.com",
                name="Demo Traveler",
                picture_url="https://api.dicebear.com/7.x/avataaars/svg?seed=Demo"
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)

        # 2. Create Community Entry for Sylhet
        entry = db.query(CommunityEntry).filter(CommunityEntry.location == "Sylhet").first()
        if not entry:
            entry = CommunityEntry(
                user_id=demo_user.id,
                name="Ratargul Swamp Forest",
                location="Sylhet",
                travel_tips="The only freshwater swamp forest in Bangladesh. Best visited during monsoon.",
                category="attraction",
                tags=["hidden_gem", "monsoon_special"],
                amenities=["Boat Trip", "Wildlife", "Photography"],
                price_range="budget",
            )
            db.add(entry)
            db.commit()
            db.refresh(entry)

        # 3. Add Nomad Metrics
        metric = db.query(NomadMetric).filter(NomadMetric.entry_id == entry.id).first()
        if not metric:
            metric = NomadMetric(
                entry_id=entry.id,
                user_id=demo_user.id,
                carrier="Grameenphone",
                signal_strength="4G High",
                safety_rating=5,
                bkash_available=True
            )
            db.add(metric)

        # 4. Add Transit Blueprints
        blueprint = db.query(TransitBlueprint).filter(TransitBlueprint.destination == "Ratargul").first()
        if not blueprint:
            blueprint = TransitBlueprint(
                user_id=demo_user.id,
                origin="Sylhet City",
                destination="Ratargul",
                raw_description="Take a local CNG from Ambarkhana bus stand to Goyainghat. Then hire a small boat for the forest entry.",
                estimated_duration_mins=90,
                estimated_cost_bdt=400.0,
                notes="Recommended to go in a group to share boat costs."
            )
            db.add(blueprint)

        # 5. Add Emergency Facility
        facility = db.query(EmergencyFacility).filter(EmergencyFacility.district == "Sylhet").first()
        if not facility:
            facility = EmergencyFacility(
                name="Sylhet MAG Osmani Medical College",
                facility_type="hospital",
                address="Osmani Medical College Road, Sylhet",
                district="Sylhet",
                latitude=24.8997,
                longitude=91.8510,
                phone_number="+880 821-714400"
            )
            db.add(facility)

        # 6. Create Itinerary
        itinerary = db.query(Itinerary).filter(Itinerary.user_id == demo_user.id, Itinerary.destination == "Sylhet").first()
        if not itinerary:
            itinerary = Itinerary(
                user_id=demo_user.id,
                destination="Sylhet",
                duration_days=3,
                budget=8000,
                travel_style="adventure",
                interests=["nature", "photography"],
                group_type="solo"
            )
            db.add(itinerary)
            db.commit()
            db.refresh(itinerary)


            # Add sample activities
            activities = [
                ItineraryActivity(itinerary_id=itinerary.id, day_number=1, start_time="09:00", end_time="11:00", title="Arrival & Hotel Check-in", location="Sylhet City", description="Check-in and freshen up.", category="rest"),
                ItineraryActivity(itinerary_id=itinerary.id, day_number=1, start_time="14:00", end_time="18:00", title="Hazrat Shahjalal Mazar", location="Dargah Gate", description="Visit the historical shrine.", category="sightseeing"),
                ItineraryActivity(itinerary_id=itinerary.id, day_number=2, start_time="08:00", end_time="14:00", title="Ratargul Swamp Forest", location="Goyainghat", description="Boat trip through the swamp forest.", estimated_cost=500, category="activity"),
            ]
            db.add_all(activities)

        db.commit()
        print("Demo data seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
