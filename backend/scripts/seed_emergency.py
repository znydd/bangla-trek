import sys
import os

# Add the backend directory to sys.path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.emergency_facility import EmergencyFacility


def seed():
    db = SessionLocal()
    try:
        # Clear existing facilities to avoid duplicates if run multiple times
        db.query(EmergencyFacility).delete()
        db.commit()

        facilities_data = [
            # ── Hospitals ──
            {
                "name": "Dhaka Medical College Hospital",
                "facility_type": "hospital",
                "address": "Secretariat Road, Dhaka 1000",
                "district": "Dhaka",
                "latitude": 23.7260,
                "longitude": 90.3978,
                "phone_number": "02-55165088",
                "notes": "Largest public hospital in Bangladesh. 24/7 emergency department.",
            },
            {
                "name": "Chittagong Medical College Hospital",
                "facility_type": "hospital",
                "address": "K.B. Fazlul Kader Road, Chittagong",
                "district": "Chittagong",
                "latitude": 22.3590,
                "longitude": 91.8318,
                "phone_number": "031-630335",
                "notes": "Major public hospital in Chittagong. Emergency services available 24/7.",
            },
            {
                "name": "Sylhet MAG Osmani Medical College Hospital",
                "facility_type": "hospital",
                "address": "Medical College Road, Sylhet 3100",
                "district": "Sylhet",
                "latitude": 24.8949,
                "longitude": 91.8687,
                "phone_number": "0821-716970",
                "notes": "Main hospital for the Sylhet division. Has emergency and trauma center.",
            },
            {
                "name": "Cox's Bazar Sadar Hospital",
                "facility_type": "hospital",
                "address": "Hospital Road, Cox's Bazar",
                "district": "Cox's Bazar",
                "latitude": 21.4354,
                "longitude": 92.0058,
                "phone_number": "0341-63044",
                "notes": "District hospital. Nearest major hospital for beach tourists.",
            },
            {
                "name": "Rangamati General Hospital",
                "facility_type": "hospital",
                "address": "Hospital Road, Rangamati",
                "district": "Rangamati",
                "latitude": 22.6372,
                "longitude": 92.1988,
                "phone_number": "0351-62053",
                "notes": "Main hospital for Rangamati Hill District. Important for Sajek Valley visitors.",
            },
            {
                "name": "Khulna Medical College Hospital",
                "facility_type": "hospital",
                "address": "KDA Avenue, Khulna",
                "district": "Khulna",
                "latitude": 22.8098,
                "longitude": 89.5644,
                "phone_number": "041-720062",
                "notes": "Primary hospital for Khulna division. Gateway for Sundarbans travelers.",
            },
            {
                "name": "Srimangal Upazila Health Complex",
                "facility_type": "hospital",
                "address": "Hospital Road, Srimangal, Moulvibazar",
                "district": "Moulvibazar",
                "latitude": 24.3065,
                "longitude": 91.7296,
                "phone_number": "08626-71021",
                "notes": "Local health complex near Lawachara National Park area.",
            },
            # ── Police Stations ──
            {
                "name": "Dhaka Metropolitan Police HQ",
                "facility_type": "police_station",
                "address": "36, Shahid Captain Mansur Ali Sarani, Dhaka",
                "district": "Dhaka",
                "latitude": 23.7372,
                "longitude": 90.4059,
                "phone_number": "02-9556990",
                "notes": "Main police headquarters for Dhaka city. Call 999 for emergencies.",
            },
            {
                "name": "Chittagong Metropolitan Police",
                "facility_type": "police_station",
                "address": "Police Line, Dampara, Chittagong",
                "district": "Chittagong",
                "latitude": 22.3350,
                "longitude": 91.8234,
                "phone_number": "031-2855998",
                "notes": "Central police station for Chittagong metro area.",
            },
            {
                "name": "Cox's Bazar Sadar Police Station",
                "facility_type": "police_station",
                "address": "Police Line Road, Cox's Bazar",
                "district": "Cox's Bazar",
                "latitude": 21.4520,
                "longitude": 91.9710,
                "phone_number": "0341-62244",
                "notes": "Main police station in Cox's Bazar town.",
            },
            {
                "name": "Sylhet Kotwali Police Station",
                "facility_type": "police_station",
                "address": "East Dargah Gate, Sylhet",
                "district": "Sylhet",
                "latitude": 24.8963,
                "longitude": 91.8712,
                "phone_number": "0821-714444",
                "notes": "Central police station in Sylhet city.",
            },
            {
                "name": "Bandarban Sadar Police Station",
                "facility_type": "police_station",
                "address": "Sadar Road, Bandarban",
                "district": "Bandarban",
                "latitude": 22.1953,
                "longitude": 92.2184,
                "phone_number": "0361-62833",
                "notes": "Main police station for Bandarban hill district.",
            },
            {
                "name": "Khagrachhari Sadar Police Station",
                "facility_type": "police_station",
                "address": "Sadar Road, Khagrachhari",
                "district": "Khagrachhari",
                "latitude": 23.1193,
                "longitude": 91.9847,
                "phone_number": "0371-61222",
                "notes": "Important for travelers heading to Sajek Valley.",
            },
            # ── Tourist Police ──
            {
                "name": "Tourist Police HQ Dhaka",
                "facility_type": "tourist_police",
                "address": "Dhaka Tourist Zone, Gulshan",
                "district": "Dhaka",
                "latitude": 23.7806,
                "longitude": 90.4193,
                "phone_number": "01769-690730",
                "notes": "National Tourist Police headquarters. Call for any tourism-related emergency. Hotline: 01769-690730.",
            },
            {
                "name": "Tourist Police Cox's Bazar",
                "facility_type": "tourist_police",
                "address": "Laboni Beach Point, Cox's Bazar",
                "district": "Cox's Bazar",
                "latitude": 21.4272,
                "longitude": 91.9790,
                "phone_number": "01769-690731",
                "notes": "Beach patrol and tourist assistance. Active along Laboni and Sugandha beach areas.",
            },
            {
                "name": "Tourist Police Sylhet",
                "facility_type": "tourist_police",
                "address": "Jindabazar, Sylhet",
                "district": "Sylhet",
                "latitude": 24.8994,
                "longitude": 91.8710,
                "phone_number": "01769-690732",
                "notes": "Covers Sylhet division including Srimangal, Ratargul, and Jaflong areas.",
            },
            {
                "name": "Tourist Police Chittagong",
                "facility_type": "tourist_police",
                "address": "GEC Circle, Chittagong",
                "district": "Chittagong",
                "latitude": 22.3569,
                "longitude": 91.8237,
                "phone_number": "01769-690733",
                "notes": "Covers Chittagong division including hill districts.",
            },
            {
                "name": "Tourist Police Khulna",
                "facility_type": "tourist_police",
                "address": "KDA Avenue, Khulna",
                "district": "Khulna",
                "latitude": 22.8200,
                "longitude": 89.5500,
                "phone_number": "01769-690734",
                "notes": "Covers Khulna division including Sundarbans entry points.",
            },
            {
                "name": "Tourist Police Rajshahi",
                "facility_type": "tourist_police",
                "address": "Saheb Bazar, Rajshahi",
                "district": "Rajshahi",
                "latitude": 24.3745,
                "longitude": 88.6042,
                "phone_number": "01769-690735",
                "notes": "Covers Rajshahi division including Paharpur and Somapura Vihara.",
            },
        ]

        for data in facilities_data:
            db.add(EmergencyFacility(**data))

        db.commit()
        print(f"Successfully seeded {len(facilities_data)} emergency facilities!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
