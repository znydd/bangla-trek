import sys
import os

# Add the backend directory to sys.path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.transit_blueprint import TransitBlueprint, TransitBlueprintStep


def seed():
    db = SessionLocal()
    try:
        # 1. Get the existing user
        user = db.query(User).first()
        if not user:
            print("No users found. Please login once via the frontend to create a user.")
            return

        user_id = user.id
        print(f"Seeding transit blueprints for user: {user.name} ({user_id})")

        # 2. Clear existing blueprints to avoid duplicates if run multiple times
        db.query(TransitBlueprintStep).delete()
        db.query(TransitBlueprint).delete()
        db.commit()

        # 3. Sample Blueprints
        blueprints_data = [
            {
                "origin": "Dhaka",
                "destination": "Sajek Valley",
                "raw_description": "Take a Shanti Paribahan bus from Dhaka Fakirapool to Khagrachhari, costs around 700 taka and takes about 7 hours. From Khagrachhari bus stand, hire a Chander Gari (jeep) going to Sajek. The jeep costs 5000-6000 taka per vehicle (can fit 8-10 people). It's a 2.5 hour bumpy ride through hills. You need a military checkpoint entry pass at Baghaichhari - the jeep driver will help you get it.",
                "estimated_duration_mins": 570,
                "estimated_cost_bdt": 1400,
                "notes": "Chander Gari prices are per vehicle so split with other travelers. The road is very rough - avoid during heavy rain. Army checkpoint closes after 5 PM, plan accordingly.",
                "steps": [
                    {"step_number": 1, "instruction": "Take a Shanti Paribahan AC bus from Dhaka Fakirapool bus counter to Khagrachhari. Buses depart at 9PM and 10PM (night coaches). Journey takes around 7 hours.", "mode": "bus", "estimated_duration_mins": 420, "estimated_cost_bdt": 700},
                    {"step_number": 2, "instruction": "From Khagrachhari bus stand, hire a Chander Gari (4WD jeep) to Sajek Valley. Wait at the stand and group up with other travelers to share the cost (5000-6000 BDT per vehicle).", "mode": "car", "estimated_duration_mins": 30, "estimated_cost_bdt": 0},
                    {"step_number": 3, "instruction": "Stop at the Baghaichhari army checkpoint to get your entry pass. The jeep driver will handle the registration. Keep your NID/passport ready.", "mode": "walking", "estimated_duration_mins": 20, "estimated_cost_bdt": 0},
                    {"step_number": 4, "instruction": "Continue the jeep ride from Baghaichhari through the winding hill roads to Sajek Valley. The road is unpaved and very bumpy but the views are stunning.", "mode": "car", "estimated_duration_mins": 100, "estimated_cost_bdt": 700},
                ]
            },
            {
                "origin": "Sylhet",
                "destination": "Ratargul Swamp Forest",
                "raw_description": "From Sylhet city, take a CNG auto-rickshaw to Salutikar (costs about 150 taka, 30 minutes). Then hire a small country boat from Salutikar ghat. The boat ride through the swamp forest takes about 2 hours and costs 500-800 taka for the whole boat. You can also take a shared boat for 100 taka per person.",
                "estimated_duration_mins": 150,
                "estimated_cost_bdt": 650,
                "notes": "Best during monsoon season (June-September) when water levels are high. Wear waterproof shoes. The boat ride is magical with submerged trees all around you.",
                "steps": [
                    {"step_number": 1, "instruction": "Take a CNG auto-rickshaw from Sylhet city (near Zindabazar) to Salutikar boat ghat. Negotiate the fare before starting.", "mode": "cng", "estimated_duration_mins": 30, "estimated_cost_bdt": 150},
                    {"step_number": 2, "instruction": "At Salutikar ghat, hire a small wooden country boat. A private boat costs 500-800 BDT, or join a shared boat for 100 BDT per person. The boatman will take you through the swamp forest.", "mode": "boat", "estimated_duration_mins": 120, "estimated_cost_bdt": 500},
                ]
            },
            {
                "origin": "Dhaka",
                "destination": "Sundarbans (Mongla Entry)",
                "raw_description": "From Dhaka Sadarghat launch terminal, take an overnight launch to Mongla. The launch departs at 5PM and arrives at Mongla around 5AM next morning. Deck class costs 400 taka, cabin 1200-2500 taka. From Mongla, hire a local trawler or join a tour group to enter Sundarbans. You need a Forest Department permit from the Mongla range office.",
                "estimated_duration_mins": 780,
                "estimated_cost_bdt": 2700,
                "notes": "Book cabin class in advance for comfort. The launch journey itself is a great experience - beautiful river views. Don't go solo into Sundarbans, always hire a licensed guide. Permit costs 150 BDT per person.",
                "steps": [
                    {"step_number": 1, "instruction": "Go to Dhaka Sadarghat launch terminal. Take a rickshaw from nearby if needed. Arrive at least 1 hour before departure to find your launch.", "mode": "rickshaw", "estimated_duration_mins": 30, "estimated_cost_bdt": 50},
                    {"step_number": 2, "instruction": "Board the overnight launch to Mongla. Launches depart around 5PM daily. Deck class 400 BDT, single cabin 1200-1500 BDT, double cabin 2000-2500 BDT. The journey is approximately 12 hours.", "mode": "launch", "estimated_duration_mins": 720, "estimated_cost_bdt": 1500},
                    {"step_number": 3, "instruction": "Arrive at Mongla around 5AM. Walk to the Forest Department Range Office to obtain your Sundarbans entry permit (150 BDT per person).", "mode": "walking", "estimated_duration_mins": 15, "estimated_cost_bdt": 150},
                    {"step_number": 4, "instruction": "Hire a trawler or join a organized tour group from Mongla jetty to enter Sundarbans. Trawler costs vary by duration (half-day around 3000-5000 BDT, full tour 8000-15000 BDT for the group).", "mode": "boat", "estimated_duration_mins": 15, "estimated_cost_bdt": 1000},
                ]
            },
            {
                "origin": "Chittagong",
                "destination": "Koh Phayam Beach (Teknaf)",
                "raw_description": "Take a Soudia bus from Chittagong New Market to Cox's Bazar, 6 hours, 600 taka. From Cox's Bazar bus stand take a local bus to Teknaf which is 2 hours 150 taka. From Teknaf town walk or take a rickshaw to the beach area.",
                "estimated_duration_mins": 510,
                "estimated_cost_bdt": 800,
                "notes": "Teknaf is close to the Myanmar border - carry your NID. The beach is very quiet and less touristy compared to Cox's Bazar. Stock up on food and water in Teknaf town.",
                "steps": [
                    {"step_number": 1, "instruction": "Take a Soudia or S. Alam bus from Chittagong New Market bus stand to Cox's Bazar. AC buses cost 600-800 BDT. Journey takes about 6 hours.", "mode": "bus", "estimated_duration_mins": 360, "estimated_cost_bdt": 600},
                    {"step_number": 2, "instruction": "From Cox's Bazar central bus stand, take a local bus heading to Teknaf. Buses run frequently throughout the day. Costs around 150 BDT, takes about 2 hours along the marine drive.", "mode": "bus", "estimated_duration_mins": 120, "estimated_cost_bdt": 150},
                    {"step_number": 3, "instruction": "From Teknaf town bus stop, take a battery-powered rickshaw or walk to the beach area. It's about a 15-minute walk.", "mode": "rickshaw", "estimated_duration_mins": 15, "estimated_cost_bdt": 30},
                ]
            },
            {
                "origin": "Srimangal",
                "destination": "Lawachara National Park",
                "raw_description": "From Srimangal town bus stand, hire a CNG auto-rickshaw for 80-100 taka. It's a 20-minute ride to the park entrance. Alternatively, you can take a shared tempo for 20 taka per person. From the main gate, walk along the trail.",
                "estimated_duration_mins": 45,
                "estimated_cost_bdt": 100,
                "notes": "Entry fee is 20 BDT for locals. Hiring a local guide (300-500 BDT) is recommended to spot the Hoolock Gibbons. Morning visits (6-8 AM) have the best chance of wildlife sightings.",
                "steps": [
                    {"step_number": 1, "instruction": "From Srimangal bus stand, hire a CNG auto-rickshaw to Lawachara National Park main entrance. Negotiate fare of 80-100 BDT. Or take a shared tempo for 20 BDT per person.", "mode": "cng", "estimated_duration_mins": 20, "estimated_cost_bdt": 80},
                    {"step_number": 2, "instruction": "Walk from the main gate along the forest trail to the interior sections. The main trail is well-marked. Consider hiring a local guide at the entrance for 300-500 BDT.", "mode": "walking", "estimated_duration_mins": 25, "estimated_cost_bdt": 20},
                ]
            },
        ]

        for data in blueprints_data:
            steps_data = data.pop("steps")

            blueprint = TransitBlueprint(
                user_id=user_id,
                origin=data["origin"],
                destination=data["destination"],
                raw_description=data["raw_description"],
                estimated_duration_mins=data.get("estimated_duration_mins"),
                estimated_cost_bdt=data.get("estimated_cost_bdt"),
                notes=data.get("notes"),
            )
            db.add(blueprint)
            db.flush()  # Get blueprint.id

            for step in steps_data:
                db.add(TransitBlueprintStep(**step, blueprint_id=blueprint.id))

        db.commit()
        print(f"Successfully seeded {len(blueprints_data)} transit blueprints!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
