import json

BASE_URL = "http://127.0.0.1:8000/api/v1"


def create_collection(name, items):
    return {
        "info": {
            "name": name,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": items,
        "variable": [{"key": "base_url", "value": BASE_URL, "type": "string"}],
    }


def create_request(name, method, path, body=None, user_id="demo_user"):
    req = {
        "name": name,
        "request": {
            "method": method,
            "header": [{"key": "X-User-Id", "value": user_id, "type": "text"}],
            "url": {
                "raw": f"{{{{base_url}}}}{path}",
                "host": ["{{base_url}}"],
                "path": [p for p in path.split("/") if p],
            },
        },
        "response": [],
    }

    if body:
        req["request"]["body"] = {
            "mode": "raw",
            "raw": json.dumps(body, indent=4),
            "options": {"raw": {"language": "json"}},
        }

    return req


member1_items = [
    {
        "name": "Community Contributions",
        "item": [
            create_request(
                "Create Contribution",
                "POST",
                "/community/contributions",
                {
                    "category": "attraction",
                    "name": "New Secret Waterfall",
                    "district": "Sylhet",
                    "latitude": 24.8949,
                    "longitude": 91.8687,
                    "price_range_min": 0,
                    "price_range_max": 200,
                    "amenities": ["Parking", "Guide"],
                    "tags": ["Hidden Gem"],
                },
            ),
            create_request("List Contributions", "GET", "/community/contributions"),
            create_request(
                "Get Contribution", "GET", "/community/contributions/contrib_101"
            ),
            create_request(
                "Update Contribution",
                "PATCH",
                "/community/contributions/contrib_101",
                {"tips": "Updated tip: Go early in the morning!"},
            ),
            create_request(
                "Delete Contribution", "DELETE", "/community/contributions/contrib_101"
            ),
        ],
    },
    {
        "name": "Group Trips",
        "item": [
            create_request(
                "Create Group Trip",
                "POST",
                "/group-trips",
                {
                    "trip_name": "Cox's Bazar Getaway",
                    "destination": "Cox's Bazar",
                    "start_date": "2026-12-01",
                    "end_date": "2026-12-05",
                    "visibility": "public",
                },
            ),
            create_request("Get My Trips", "GET", "/group-trips/my"),
            create_request(
                "Get Overlapping Travelers",
                "GET",
                "/group-trips/overlapping-travelers?destination=Sajek Valley&start_date=2025-06-10&end_date=2025-06-14",
            ),
            create_request("Get Trip Detail", "GET", "/group-trips/group_201"),
            create_request(
                "Join Trip",
                "POST",
                "/group-trips/join",
                {"invite_code": "SAJEK2025XYZ"},
                user_id="user_new",
            ),
            create_request(
                "Update Trip",
                "PATCH",
                "/group-trips/group_201",
                {"description": "Updated relaxed trip"},
            ),
            create_request(
                "Generate Invite Link", "POST", "/group-trips/group_201/invite-link"
            ),
            create_request("Delete Trip", "DELETE", "/group-trips/group_201"),
        ],
    },
]

member2_items = [
    {
        "name": "AI Itinerary",
        "item": [
            create_request(
                "Generate Itinerary",
                "POST",
                "/itineraries/generate",
                {
                    "destination": "Sylhet",
                    "duration_days": 3,
                    "budget": 15000,
                    "travel_styles": ["Adventure"],
                    "interests": ["Nature", "Food"],
                    "prioritize_hidden_gems": True,
                },
            ),
            create_request(
                "Save Itinerary",
                "POST",
                "/itineraries",
                {
                    "generated_itinerary_id": "iti_301",
                    "trip_name": "My Saved Sylhet Trip",
                },
            ),
            create_request("Get Saved Itinerary", "GET", "/itineraries/saved_301"),
            create_request(
                "Update Itinerary",
                "PATCH",
                "/itineraries/saved_301",
                {"notes": "Need to bring extra hiking boots."},
            ),
            create_request("Delete Itinerary", "DELETE", "/itineraries/saved_301"),
        ],
    },
    {
        "name": "Accommodation",
        "item": [
            create_request(
                "Get Recommendations",
                "GET",
                "/accommodations/recommendations?destination=Sajek Valley",
            ),
            create_request(
                "Get AI Top Pick",
                "POST",
                "/accommodations/ai-top-pick",
                {
                    "destination": "Sajek Valley",
                    "budget_per_night": 3000,
                    "preferred_amenities": ["WiFi", "Local Meals"],
                },
            ),
            create_request(
                "Get Accommodation Detail", "GET", "/accommodations/acc_401"
            ),
        ],
    },
]

member3_items = [
    {
        "name": "Nomad Metrics",
        "item": [
            create_request(
                "Get Nomad Metrics", "GET", "/locations/loc_5002/nomad-metrics"
            ),
            create_request(
                "Get Nomad Map", "GET", "/locations/loc_5002/nomad-map?layer=network"
            ),
            create_request(
                "List Ratings", "GET", "/locations/loc_5002/nomad-metrics/ratings"
            ),
            create_request(
                "Create Rating",
                "POST",
                "/locations/loc_5002/nomad-metrics/ratings",
                {
                    "carrier_reports": [{"carrier": "Banglalink", "signal": "4g"}],
                    "solo_female_safety_score": 4.5,
                    "digital_payment_reports": {"bkash": "Available"},
                    "general_infrastructure": {"road_quality": 3},
                },
                user_id="user_new",
            ),
            create_request(
                "Update Rating",
                "PATCH",
                "/locations/loc_5002/nomad-metrics/ratings/<rating_id>",
                {"solo_female_safety_score": 5.0},
            ),
            create_request(
                "Delete Rating",
                "DELETE",
                "/locations/loc_5002/nomad-metrics/ratings/<rating_id>",
            ),
        ],
    },
    {
        "name": "Budget Tracker",
        "item": [
            create_request(
                "Create Budget",
                "POST",
                "/trips/group_201/budget",
                {
                    "total_budget": 25000,
                    "category_allocations": {"food": 5000, "transport": 5000},
                },
                user_id="user_new",
            ),  # Assuming previous budget is deleted or testing new
            create_request("Get Budget Summary", "GET", "/trips/group_201/budget"),
            create_request(
                "Add Expense",
                "POST",
                "/trips/group_201/budget/expenses",
                {
                    "amount": 500,
                    "category": "food",
                    "description": "Lunch at local spot",
                    "expense_date": "2025-06-10",
                },
            ),
            create_request("Get Expenses", "GET", "/trips/group_201/budget/expenses"),
            create_request(
                "Get Budget Analytics", "GET", "/trips/group_201/budget/analytics"
            ),
            create_request(
                "Update Expense",
                "PATCH",
                "/trips/group_201/budget/expenses/exp_1001",
                {"amount": 900},
            ),
            create_request(
                "Delete Expense", "DELETE", "/trips/group_201/budget/expenses/exp_1001"
            ),
        ],
    },
]

member4_items = [
    {
        "name": "Chatbot Refinement",
        "item": [
            create_request(
                "Send Chat Message",
                "POST",
                "/itineraries/saved_301/chat",
                {
                    "message": "Can we make it more focused on nature?",
                    "context_version": 1,
                },
            ),
            create_request(
                "Apply Changes",
                "POST",
                "/itineraries/saved_301/chat/apply",
                {"accepted_change_ids": ["<replace_with_change_id_from_response>"]},
            ),
            create_request(
                "Get Chat History", "GET", "/itineraries/saved_301/chat/history"
            ),
            create_request(
                "Get Seasonal Alert",
                "GET",
                "/seasonal-alerts?destination=Sylhet&travel_month=July",
            ),
        ],
    },
    {
        "name": "Collaborative Planning",
        "item": [
            create_request("Get Itinerary", "GET", "/group-trips/group_201/itinerary"),
            create_request(
                "Add Activity",
                "POST",
                "/group-trips/group_201/itinerary/activities",
                {"day": 2, "title": "Visit waterfall", "time": "10:00"},
            ),
            create_request(
                "Update Activity",
                "PATCH",
                "/group-trips/group_201/itinerary/activities/act_1",
                {"title": "Reach Sajek earlier"},
            ),
            create_request(
                "Delete Activity",
                "DELETE",
                "/group-trips/group_201/itinerary/activities/act_1",
            ),
            create_request(
                "Upsert Presence",
                "POST",
                "/group-trips/group_201/presence",
                {"status": "online", "editing_target": "Day 1"},
            ),
            create_request("Get Presence", "GET", "/group-trips/group_201/presence"),
            create_request(
                "Create Poll",
                "POST",
                "/group-trips/group_201/polls",
                {
                    "question": "Which resort for day 3?",
                    "type": "accommodation",
                    "options": [{"label": "Resort A"}, {"label": "Resort B"}],
                },
            ),
            create_request(
                "Vote on Poll",
                "POST",
                "/group-trips/group_201/polls/poll_11/vote",
                {"option_id": "opt_1"},
            ),
            create_request("List Polls", "GET", "/group-trips/group_201/polls"),
            create_request(
                "Get Activity Feed", "GET", "/group-trips/group_201/activity-feed"
            ),
        ],
    },
]

with open("Member1_Community_GroupTrips.postman_collection.json", "w") as f:
    json.dump(create_collection("Bangla Trek - Member 1", member1_items), f, indent=2)

with open("Member2_AI_Itinerary_Accommodation.postman_collection.json", "w") as f:
    json.dump(create_collection("Bangla Trek - Member 2", member2_items), f, indent=2)

with open("Member3_NomadMetrics_Budget.postman_collection.json", "w") as f:
    json.dump(create_collection("Bangla Trek - Member 3", member3_items), f, indent=2)

with open("Member4_Chatbot_Collaboration.postman_collection.json", "w") as f:
    json.dump(create_collection("Bangla Trek - Member 4", member4_items), f, indent=2)

print("Collections generated.")
