# BongoVromon API Specification

This document defines the API specification for the **8 selected features** shown in the current UI plan. The APIs are grouped under their corresponding member names, with **2 features per member**.

## General API Conventions

- **Base URL:** `/api/v1`
- **Auth:** Most endpoints require user authentication via bearer token/session unless marked public.
- **Content-Type:** `application/json`
- **File Uploads:** Image uploads should use Cloudinary; backend stores returned URLs.
- **Timestamps:** ISO 8601 format
- **Currency:** BDT
- **Pagination:** `page`, `limit`
- **Standard success response format:**

```bongovromon/api.md#L13-23
{
  "success": true,
  "message": "Human-readable response message",
  "data": {},
  "meta": {
    "page": 1,
    "limit": 10,
    "total": 100
  }
}
```

- **Standard error response format:**

```bongovromon/api.md#L25-32
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "field_name": ["Error message"]
  }
}
```

---

# Member-1 APIs

## Feature 1: Community Data Contribution Page

Allows users to contribute attractions, hotels, guesthouses, homestays, and restaurants with metadata, media, tags, and travel tips.

### 1. Create Community Contribution
**Endpoint:** `POST /community/contributions`

**What it does:**
Creates a new place contribution submitted by a user.

**Request Body:**

```bongovromon/api.md#L44-59
{
  "category": "attraction",
  "name": "Niladri Lake",
  "district": "Sunamganj",
  "upazila": "Tahirpur",
  "address": "Tekerghat, Tahirpur, Sunamganj",
  "latitude": 25.1142,
  "longitude": 91.0023,
  "price_range_min": 100,
  "price_range_max": 800,
  "amenities": ["Boat Ride", "Parking", "Food Stalls"],
  "tips": "Visit early morning for the best light and fewer crowds.",
  "photo_urls": [
    "https://res.cloudinary.com/demo/image/upload/v1/niladri1.jpg"
  ],
  "embedded_video_urls": [
    "https://www.youtube.com/watch?v=abcd1234"
  ],
  "tags": ["Hidden Gem"]
}
```

**Response Data:**

```bongovromon/api.md#L61-81
{
  "success": true,
  "message": "Contribution created successfully",
  "data": {
    "id": "contrib_101",
    "user_id": "user_12",
    "category": "attraction",
    "name": "Niladri Lake",
    "district": "Sunamganj",
    "upazila": "Tahirpur",
    "address": "Tekerghat, Tahirpur, Sunamganj",
    "coordinates": {
      "latitude": 25.1142,
      "longitude": 91.0023
    },
    "price_range": {
      "min": 100,
      "max": 800
    },
    "amenities": ["Boat Ride", "Parking", "Food Stalls"],
    "tips": "Visit early morning for the best light and fewer crowds.",
    "photo_urls": ["https://res.cloudinary.com/demo/image/upload/v1/niladri1.jpg"],
    "embedded_video_urls": ["https://www.youtube.com/watch?v=abcd1234"],
    "tags": ["Hidden Gem"],
    "status": "pending_review",
    "created_at": "2025-03-12T10:30:00Z"
  }
}
```

### 2. Get Contribution List
**Endpoint:** `GET /community/contributions?category=attraction&district=Sunamganj&tag=Hidden%20Gem&page=1&limit=10`

**What it does:**
Returns a filtered list of contributed places.

**Response Example:**

```bongovromon/api.md#L87-112
{
  "success": true,
  "message": "Contributions fetched successfully",
  "data": [
    {
      "id": "contrib_101",
      "name": "Niladri Lake",
      "category": "attraction",
      "district": "Sunamganj",
      "thumbnail_url": "https://res.cloudinary.com/demo/image/upload/v1/niladri1.jpg",
      "price_range": {
        "min": 100,
        "max": 800
      },
      "tags": ["Hidden Gem"],
      "average_rating": 4.7
    },
    {
      "id": "contrib_102",
      "name": "Ratargul Watch Tower",
      "category": "attraction",
      "district": "Sylhet",
      "thumbnail_url": "https://res.cloudinary.com/demo/image/upload/v1/ratargul.jpg",
      "price_range": {
        "min": 50,
        "max": 300
      },
      "tags": ["Trending"],
      "average_rating": 4.4
    }
  ],
  "meta": {
    "page": 1,
    "limit": 10,
    "total": 2
  }
}
```

### 3. Get Single Contribution Details
**Endpoint:** `GET /community/contributions/{id}`

**What it does:**
Returns full details of one contributed place for its location/detail page.

### 4. Update Contribution
**Endpoint:** `PATCH /community/contributions/{id}`

**What it does:**
Updates editable fields of a contribution by the owner/admin.

**Example Request:**

```bongovromon/api.md#L122-129
{
  "price_range_min": 150,
  "price_range_max": 900,
  "tips": "Carry cash because digital payment is not always available.",
  "tags": ["Hidden Gem", "Trending"]
}
```

### 5. Delete Contribution
**Endpoint:** `DELETE /community/contributions/{id}`

**What it does:**
Deletes a contribution by owner/admin.

**Example Response:**

```bongovromon/api.md#L137-142
{
  "success": true,
  "message": "Contribution deleted successfully",
  "data": null
}
```

---

## Feature 2: Group Trip Creation Page

Allows users to create group trips, choose visibility, generate invite links, and discover overlapping travelers.

### 1. Create Group Trip
**Endpoint:** `POST /group-trips`

**What it does:**
Creates a new public/private group trip.

**Request Body:**

```bongovromon/api.md#L153-161
{
  "trip_name": "Sajek Friends Tour",
  "destination": "Sajek Valley",
  "start_date": "2025-06-10",
  "end_date": "2025-06-14",
  "visibility": "public",
  "description": "A 4-night relaxed trip with nature, food, and photography focus."
}
```

**Response Example:**

```bongovromon/api.md#L163-181
{
  "success": true,
  "message": "Group trip created successfully",
  "data": {
    "id": "group_201",
    "trip_name": "Sajek Friends Tour",
    "destination": "Sajek Valley",
    "start_date": "2025-06-10",
    "end_date": "2025-06-14",
    "visibility": "public",
    "description": "A 4-night relaxed trip with nature, food, and photography focus.",
    "created_by": "user_12",
    "invite_code": "SAJEK2025XYZ",
    "invite_link": "https://bongovromon.com/groups/join/SAJEK2025XYZ",
    "member_count": 1,
    "created_at": "2025-03-12T11:00:00Z"
  }
}
```

### 2. Get My Group Trips
**Endpoint:** `GET /group-trips/my?page=1&limit=10`

**What it does:**
Returns the authenticated user’s group trips.

**Example Response:**

```bongovromon/api.md#L187-208
{
  "success": true,
  "message": "Group trips fetched successfully",
  "data": [
    {
      "id": "group_201",
      "trip_name": "Sajek Friends Tour",
      "destination": "Sajek Valley",
      "start_date": "2025-06-10",
      "end_date": "2025-06-14",
      "visibility": "public",
      "member_count": 5,
      "cover_image_url": "https://res.cloudinary.com/demo/image/upload/v1/sajek-cover.jpg"
    },
    {
      "id": "group_202",
      "trip_name": "Sylhet Tea Escape",
      "destination": "Sylhet",
      "start_date": "2025-07-03",
      "end_date": "2025-07-06",
      "visibility": "private",
      "member_count": 3,
      "cover_image_url": "https://res.cloudinary.com/demo/image/upload/v1/sylhet-cover.jpg"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 10,
    "total": 2
  }
}
```

### 3. Generate / Refresh Invite Link
**Endpoint:** `POST /group-trips/{groupTripId}/invite-link`

**What it does:**
Generates or refreshes a shareable invite link.

**Example Response:**

```bongovromon/api.md#L216-224
{
  "success": true,
  "message": "Invite link generated successfully",
  "data": {
    "invite_code": "SAJEKNEW456",
    "invite_link": "https://bongovromon.com/groups/join/SAJEKNEW456"
  }
}
```

### 4. Join Group Trip via Invite
**Endpoint:** `POST /group-trips/join`

**Request Body:**

```bongovromon/api.md#L230-234
{
  "invite_code": "SAJEK2025XYZ"
}
```

### 5. Find Overlapping Travelers
**Endpoint:** `GET /group-trips/overlapping-travelers?destination=Sajek%20Valley&start_date=2025-06-10&end_date=2025-06-14`

**What it does:**
Returns travelers with overlapping destination and date ranges.

**Example Response:**

```bongovromon/api.md#L240-263
{
  "success": true,
  "message": "Overlapping travelers fetched successfully",
  "data": [
    {
      "user_id": "user_88",
      "name": "Rafi",
      "avatar_url": "https://example.com/avatar/rafi.jpg",
      "travel_dates": {
        "start_date": "2025-06-11",
        "end_date": "2025-06-15"
      },
      "mutual_interests": ["Photography", "Food", "Nature"]
    },
    {
      "user_id": "user_91",
      "name": "Tania",
      "avatar_url": "https://example.com/avatar/tania.jpg",
      "travel_dates": {
        "start_date": "2025-06-09",
        "end_date": "2025-06-13"
      },
      "mutual_interests": ["Adventure", "Hiking"]
    }
  ]
}
```

---

# Member-2 APIs

## Feature 3: AI Itinerary Generation Page

Generates personalized itineraries using destination, budget, trip duration, travel style, and interests.

### 1. Generate Itinerary
**Endpoint:** `POST /itineraries/generate`

**What it does:**
Uses user inputs and community data to generate an AI-powered itinerary.

**Request Body:**

```bongovromon/api.md#L277-289
{
  "destination": "Sylhet",
  "duration_days": 3,
  "budget": 12000,
  "travel_styles": ["Budget", "Adventure"],
  "interests": ["Nature", "Photography", "Food"],
  "group_type": "Friends",
  "prioritize_hidden_gems": true
}
```

**Response Example:**

```bongovromon/api.md#L291-341
{
  "success": true,
  "message": "Itinerary generated successfully",
  "data": {
    "itinerary_id": "iti_301",
    "destination": "Sylhet",
    "duration_days": 3,
    "estimated_total_cost": 10950,
    "days": [
      {
        "day": 1,
        "theme": "Nature and Local Food",
        "activities": [
          {
            "time": "08:00",
            "title": "Breakfast at Panshi Restaurant",
            "description": "Try local Sylheti breakfast items before starting the day.",
            "estimated_cost": 180,
            "location_id": "loc_5001",
            "tags": ["Food"]
          },
          {
            "time": "11:00",
            "title": "Visit Ratargul Swamp Forest",
            "description": "Boat tour through the freshwater swamp forest.",
            "estimated_cost": 850,
            "location_id": "loc_5002",
            "tags": ["Nature", "Hidden Gem"],
            "local_cultural_insight": "Local boatmen often share stories about seasonal changes and water levels."
          }
        ]
      }
    ],
    "generated_at": "2025-03-12T11:30:00Z"
  }
}
```

### 2. Save Generated Itinerary
**Endpoint:** `POST /itineraries`

**What it does:**
Saves a generated itinerary to the user account.

**Request Body:**

```bongovromon/api.md#L347-352
{
  "generated_itinerary_id": "iti_301",
  "trip_name": "Sylhet Adventure Plan"
}
```

### 3. Get Itinerary by ID
**Endpoint:** `GET /itineraries/{itineraryId}`

**What it does:**
Returns the saved itinerary details.

### 4. Update Saved Itinerary
**Endpoint:** `PATCH /itineraries/{itineraryId}`

**What it does:**
Updates title, notes, selected activities, budget cap, or manual modifications.

### 5. Delete Itinerary
**Endpoint:** `DELETE /itineraries/{itineraryId}`

**What it does:**
Deletes a saved itinerary.

---

## Feature 4: Accommodation Recommendations Page

Returns accommodation recommendations from community data and AI ranking.

### 1. Get Accommodation Recommendations
**Endpoint:** `GET /accommodations/recommendations?destination=Sajek%20Valley&type=Hotel,Homestay&min_price=1500&max_price=5000&amenities=WiFi,Hot%20Water&min_rating=4&sort_by=distance`

**What it does:**
Returns filtered accommodation options based on destination, budget, amenities, ratings, and distance to planned attractions.

**Response Example:**

```bongovromon/api.md#L371-416
{
  "success": true,
  "message": "Accommodation recommendations fetched successfully",
  "data": {
    "items": [
      {
        "id": "acc_401",
        "name": "Megh Valley Resort",
        "type": "Hotel",
        "price_per_night": 4200,
        "star_rating": 4.5,
        "review_count": 128,
        "amenities": ["WiFi", "Hot Water", "Restaurant"],
        "distance_to_nearest_attraction_km": 1.2,
        "nearest_attraction_name": "Sajek Valley Viewpoint",
        "cover_photo_url": "https://res.cloudinary.com/demo/image/upload/v1/megh-valley.jpg",
        "coordinates": {
          "latitude": 23.3811,
          "longitude": 92.2934
        }
      },
      {
        "id": "acc_402",
        "name": "Hilltop Homestay",
        "type": "Homestay",
        "price_per_night": 2500,
        "star_rating": 4.3,
        "review_count": 54,
        "amenities": ["WiFi", "Parking", "Local Meals"],
        "distance_to_nearest_attraction_km": 0.8,
        "nearest_attraction_name": "Konglak Hill",
        "cover_photo_url": "https://res.cloudinary.com/demo/image/upload/v1/hilltop.jpg",
        "coordinates": {
          "latitude": 23.3798,
          "longitude": 92.2919
        }
      }
    ],
    "map_pins": [
      {
        "id": "acc_401",
        "type": "accommodation",
        "latitude": 23.3811,
        "longitude": 92.2934
      },
      {
        "id": "acc_402",
        "type": "accommodation",
        "latitude": 23.3798,
        "longitude": 92.2919
      }
    ]
  }
}
```

### 2. Get Accommodation Details
**Endpoint:** `GET /accommodations/{accommodationId}`

**What it does:**
Returns full accommodation details for the property details modal/page.

### 3. Get AI Top Pick
**Endpoint:** `POST /accommodations/ai-top-pick`

**What it does:**
Returns the best strategic accommodation recommendation using itinerary attractions and budget context.

**Request Body:**

```bongovromon/api.md#L424-434
{
  "destination": "Sajek Valley",
  "budget_per_night": 4500,
  "planned_attraction_ids": ["loc_7001", "loc_7002", "loc_7005"],
  "preferred_amenities": ["WiFi", "Hot Water"],
  "trip_type": "Friends"
}
```

**Response Example:**

```bongovromon/api.md#L436-453
{
  "success": true,
  "message": "AI top pick generated successfully",
  "data": {
    "accommodation_id": "acc_401",
    "name": "Megh Valley Resort",
    "price_per_night": 4200,
    "reason": "Best value based on proximity to planned attractions and strong amenity match.",
    "comparison_badges": [
      "Saves 45 min daily travel",
      "Best value in area"
    ]
  }
}
```

---

# Member-3 APIs

## Feature 5: Nomad Metrics & Interactive Map Page

Returns community-rated infrastructure metrics and allows users to submit ratings.

### 1. Get Nomad Metrics for a Location
**Endpoint:** `GET /locations/{locationId}/nomad-metrics`

**What it does:**
Returns all infrastructure and safety metrics for a given location.

**Response Example:**

```bongovromon/api.md#L466-512
{
  "success": true,
  "message": "Nomad metrics fetched successfully",
  "data": {
    "location_id": "loc_5002",
    "location_name": "Ratargul Swamp Forest",
    "network_connectivity": [
      {
        "carrier": "Grameenphone",
        "signal_levels": {
          "no_signal_votes": 2,
          "2g_votes": 5,
          "3g_votes": 21,
          "4g_votes": 10
        },
        "dominant_signal": "3G"
      },
      {
        "carrier": "Robi",
        "signal_levels": {
          "no_signal_votes": 8,
          "2g_votes": 10,
          "3g_votes": 7,
          "4g_votes": 1
        },
        "dominant_signal": "2G"
      }
    ],
    "solo_female_safety": {
      "score": 4.2,
      "rating_count": 86,
      "top_tips": [
        "Avoid very late-night travel by boat.",
        "Travel with a trusted guide during monsoon.",
        "Keep emergency contacts saved offline."
      ]
    },
    "digital_payments": {
      "bkash": { "status": "Available", "availability_percent": 78 },
      "nagad": { "status": "Limited", "availability_percent": 42 },
      "rocket": { "status": "Unavailable", "availability_percent": 10 }
    },
    "general_infrastructure": {
      "electricity_reliability": 3.4,
      "clean_water_access": 3.1,
      "road_quality": 2.9
    }
  }
}
```

### 2. Get Nomad Map Layers
**Endpoint:** `GET /locations/{locationId}/nomad-map?layer=network`

**What it does:**
Returns map overlay and pin data for the selected layer: `network`, `safety`, or `payments`.

**Response Example:**

```bongovromon/api.md#L518-546
{
  "success": true,
  "message": "Map layer fetched successfully",
  "data": {
    "location_id": "loc_5002",
    "layer": "network",
    "overlays": [
      {
        "zone_id": "zone_01",
        "label": "Strong GP 3G Area",
        "color": "#2A9D8F",
        "polygon": [
          [25.115, 91.003],
          [25.116, 91.005],
          [25.113, 91.006]
        ]
      }
    ],
    "pins": [
      {
        "poi_id": "poi_12",
        "name": "Boat Ghat",
        "latitude": 25.1149,
        "longitude": 91.0041,
        "popup_summary": "Payment mostly cash only, GP network works best here."
      }
    ]
  }
}
```

### 3. Submit Nomad Metrics Rating
**Endpoint:** `POST /locations/{locationId}/nomad-metrics/ratings`

**What it does:**
Allows authenticated users to submit their own ratings and comments.

**Request Body:**

```bongovromon/api.md#L552-565
{
  "carrier_reports": [
    { "carrier": "Grameenphone", "signal": "3G" },
    { "carrier": "Robi", "signal": "No Signal" }
  ],
  "solo_female_safety_score": 4,
  "solo_female_safety_tip": "Daytime felt safe, but public transport gets sparse after evening.",
  "digital_payment_reports": {
    "bkash": "Available",
    "nagad": "Limited",
    "rocket": "Unavailable"
  },
  "general_infrastructure": {
    "electricity_reliability": 3,
    "clean_water_access": 4,
    "road_quality": 2
  }
}
```

### 4. Update Nomad Metrics Rating
**Endpoint:** `PATCH /locations/{locationId}/nomad-metrics/ratings/{ratingId}`

### 5. Delete Nomad Metrics Rating
**Endpoint:** `DELETE /locations/{locationId}/nomad-metrics/ratings/{ratingId}`

---

## Feature 6: Live Budget Tracker Page

Lets users set trip budgets, log expenses, view charts, and receive threshold alerts.

### 1. Create Budget Tracker for Trip
**Endpoint:** `POST /trips/{tripId}/budget`

**What it does:**
Initializes a budget tracker for a trip.

**Request Body:**

```bongovromon/api.md#L578-583
{
  "total_budget": 20000,
  "category_allocations": {
    "accommodation": 7000,
    "food": 4000,
    "transport": 5000,
    "attractions": 2500,
    "shopping": 1000,
    "other": 500
  }
}
```

### 2. Get Budget Summary
**Endpoint:** `GET /trips/{tripId}/budget`

**What it does:**
Returns the current spending summary, progress percentage, remaining budget, and alerts.

**Response Example:**

```bongovromon/api.md#L591-621
{
  "success": true,
  "message": "Budget summary fetched successfully",
  "data": {
    "trip_id": "trip_901",
    "total_budget": 20000,
    "total_spent": 12400,
    "remaining_budget": 7600,
    "spent_percentage": 62,
    "status_color": "amber",
    "alerts": [
      {
        "type": "warning",
        "message": "You've used 62% of your budget."
      }
    ],
    "category_breakdown": {
      "accommodation": 5000,
      "food": 2600,
      "transport": 3100,
      "attractions": 1200,
      "shopping": 300,
      "other": 200
    },
    "daily_average_spending": 2480,
    "projected_total_spending": 18600
  }
}
```

### 3. Add Expense
**Endpoint:** `POST /trips/{tripId}/budget/expenses`

**What it does:**
Adds a new expense entry.

**Request Body:**

```bongovromon/api.md#L627-635
{
  "amount": 850,
  "category": "transport",
  "description": "CNG fare from Sreemangal station to resort",
  "expense_date": "2025-06-11",
  "receipt_photo_url": "https://res.cloudinary.com/demo/image/upload/v1/receipt123.jpg"
}
```

**Response Example:**

```bongovromon/api.md#L637-651
{
  "success": true,
  "message": "Expense added successfully",
  "data": {
    "expense_id": "exp_1001",
    "amount": 850,
    "category": "transport",
    "description": "CNG fare from Sreemangal station to resort",
    "expense_date": "2025-06-11",
    "receipt_photo_url": "https://res.cloudinary.com/demo/image/upload/v1/receipt123.jpg",
    "created_at": "2025-06-11T09:10:00Z"
  }
}
```

### 4. Get Expense Log
**Endpoint:** `GET /trips/{tripId}/budget/expenses?group_by=day`

**What it does:**
Returns expenses grouped by day for the expense list UI.

### 5. Update Expense
**Endpoint:** `PATCH /trips/{tripId}/budget/expenses/{expenseId}`

### 6. Delete Expense
**Endpoint:** `DELETE /trips/{tripId}/budget/expenses/{expenseId}`

### 7. Get Budget Analytics
**Endpoint:** `GET /trips/{tripId}/budget/analytics`

**What it does:**
Returns chart-ready data for pie chart, stacked bar chart, and daily trend chart.

**Response Example:**

```bongovromon/api.md#L665-702
{
  "success": true,
  "message": "Budget analytics fetched successfully",
  "data": {
    "pie_chart": [
      { "category": "accommodation", "amount": 5000 },
      { "category": "food", "amount": 2600 },
      { "category": "transport", "amount": 3100 },
      { "category": "attractions", "amount": 1200 },
      { "category": "shopping", "amount": 300 },
      { "category": "other", "amount": 200 }
    ],
    "allocation_vs_actual": [
      { "category": "accommodation", "allocated": 7000, "actual": 5000 },
      { "category": "food", "allocated": 4000, "actual": 2600 },
      { "category": "transport", "allocated": 5000, "actual": 3100 }
    ],
    "daily_trend": [
      { "date": "2025-06-10", "amount": 3200 },
      { "date": "2025-06-11", "amount": 4100 },
      { "date": "2025-06-12", "amount": 5100 }
    ]
  }
}
```

---

# Member-4 APIs

## Feature 7: AI Chatbot for Itinerary Refinement Page

Lets users refine itineraries using natural language and receive seasonal intelligence alerts.

### 1. Send Chat Message for Itinerary Refinement
**Endpoint:** `POST /itineraries/{itineraryId}/chat`

**What it does:**
Accepts a user prompt and returns AI suggestions plus optionally updated itinerary blocks.

**Request Body:**

```bongovromon/api.md#L715-720
{
  "message": "Add more nature spots and keep the total trip under 5000 taka.",
  "context_version": 3
}
```

**Response Example:**

```bongovromon/api.md#L722-756
{
  "success": true,
  "message": "AI response generated successfully",
  "data": {
    "reply": "I updated Day 2 to include a lower-cost nature activity and removed one expensive restaurant stop.",
    "suggested_changes": [
      {
        "type": "replace_activity",
        "day": 2,
        "old_activity": "Premium dinner at resort",
        "new_activity": "Local food market dinner"
      }
    ],
    "updated_cost_summary": {
      "previous_total": 6200,
      "new_total": 4850
    },
    "updated_itinerary_preview": [
      {
        "day": 2,
        "activities": [
          {
            "time": "16:00",
            "title": "Short forest trail walk",
            "estimated_cost": 0
          },
          {
            "time": "19:30",
            "title": "Dinner at local food market",
            "estimated_cost": 250
          }
        ]
      }
    ]
  }
}
```

### 2. Save AI Refinement Changes
**Endpoint:** `POST /itineraries/{itineraryId}/chat/apply`

**What it does:**
Applies accepted AI modifications to the saved itinerary.

**Request Body:**

```bongovromon/api.md#L762-768
{
  "accepted_change_ids": [
    "chg_01",
    "chg_02"
  ]
}
```

### 3. Get Chat History
**Endpoint:** `GET /itineraries/{itineraryId}/chat/history`

**What it does:**
Returns previous chat messages and assistant replies for this itinerary.

### 4. Get Seasonal Intelligence Alert
**Endpoint:** `GET /seasonal-alerts?destination=Sylhet&travel_month=July`

**What it does:**
Returns destination-specific seasonal warning, monsoon intelligence, and suggested best months.

**Response Example:**

```bongovromon/api.md#L777-793
{
  "success": true,
  "message": "Seasonal alert fetched successfully",
  "data": {
    "destination": "Sylhet",
    "travel_month": "July",
    "alert_level": "warning",
    "title": "Monsoon season in Sylhet",
    "summary": "Heavy rainfall expected from June to September. Some routes may be waterlogged.",
    "recommended_months": ["October", "November", "December", "January", "February"],
    "tips": [
      "Carry waterproof bags for electronics.",
      "Keep backup transport options.",
      "Check local road conditions before departure."
    ]
  }
}
```

---

## Feature 8: Collaborative Group Planning & Polling Page

Supports shared itinerary editing, polling, activity feed, and real-time collaboration updates.

### 1. Get Shared Group Itinerary
**Endpoint:** `GET /group-trips/{groupTripId}/itinerary`

**What it does:**
Returns the collaborative itinerary for the group trip.

**Response Example:**

```bongovromon/api.md#L804-835
{
  "success": true,
  "message": "Group itinerary fetched successfully",
  "data": {
    "group_trip_id": "group_201",
    "days": [
      {
        "day": 1,
        "activities": [
          {
            "activity_id": "act_1",
            "title": "Reach Sajek and check in",
            "time": "10:00",
            "added_by": {
              "user_id": "user_12",
              "name": "Nafis"
            },
            "vote_count": 4,
            "status": "confirmed"
          },
          {
            "activity_id": "act_2",
            "title": "Sunset at Konglak Hill",
            "time": "17:00",
            "added_by": {
              "user_id": "user_88",
              "name": "Rafi"
            },
            "vote_count": 3,
            "status": "under_vote"
          }
        ]
      }
    ]
  }
}
```

### 2. Add Activity to Group Itinerary
**Endpoint:** `POST /group-trips/{groupTripId}/itinerary/activities`

**What it does:**
Adds a new activity suggestion to the shared group itinerary.

**Request Body:**

```bongovromon/api.md#L841-847
{
  "day": 2,
  "title": "Lunch at local bamboo restaurant",
  "time": "13:30",
  "location_id": "loc_8004"
}
```

### 3. Update Group Itinerary Activity
**Endpoint:** `PATCH /group-trips/{groupTripId}/itinerary/activities/{activityId}`

### 4. Delete Group Itinerary Activity
**Endpoint:** `DELETE /group-trips/{groupTripId}/itinerary/activities/{activityId}`

### 5. Get Group Members Presence
**Endpoint:** `GET /group-trips/{groupTripId}/presence`

**What it does:**
Returns online/offline members and editing indicators.

**Example Response:**

```bongovromon/api.md#L857-878
{
  "success": true,
  "message": "Presence data fetched successfully",
  "data": [
    {
      "user_id": "user_12",
      "name": "Nafis",
      "status": "online",
      "role": "Organizer",
      "editing_target": "Day 2 Activity act_8",
      "presence_color": "teal"
    },
    {
      "user_id": "user_88",
      "name": "Rafi",
      "status": "offline",
      "role": "Member",
      "editing_target": null,
      "presence_color": "purple"
    }
  ]
}
```

### 6. Create Poll
**Endpoint:** `POST /group-trips/{groupTripId}/polls`

**What it does:**
Creates a poll for attraction, hotel, restaurant, or any planning decision.

**Request Body:**

```bongovromon/api.md#L884-897
{
  "question": "Where should we eat dinner on Day 2?",
  "type": "restaurant",
  "deadline": "2025-06-09T20:00:00Z",
  "options": [
    { "location_id": "loc_100", "label": "Paharika Restaurant" },
    { "location_id": "loc_101", "label": "Megh Cabin BBQ" },
    { "location_id": "loc_102", "label": "Hill View Restaurant" }
  ]
}
```

**Response Example:**

```bongovromon/api.md#L899-919
{
  "success": true,
  "message": "Poll created successfully",
  "data": {
    "poll_id": "poll_11",
    "question": "Where should we eat dinner on Day 2?",
    "type": "restaurant",
    "deadline": "2025-06-09T20:00:00Z",
    "status": "active",
    "options": [
      { "option_id": "opt_1", "label": "Paharika Restaurant", "vote_count": 0 },
      { "option_id": "opt_2", "label": "Megh Cabin BBQ", "vote_count": 0 },
      { "option_id": "opt_3", "label": "Hill View Restaurant", "vote_count": 0 }
    ]
  }
}
```

### 7. Vote on Poll
**Endpoint:** `POST /group-trips/{groupTripId}/polls/{pollId}/vote`

**Request Body:**

```bongovromon/api.md#L925-929
{
  "option_id": "opt_2"
}
```

### 8. Get Active Polls
**Endpoint:** `GET /group-trips/{groupTripId}/polls?status=active`

**What it does:**
Returns all current polls and vote summaries.

### 9. Get Group Activity Feed
**Endpoint:** `GET /group-trips/{groupTripId}/activity-feed`

**What it does:**
Returns recent collaborative actions for the activity feed.

**Response Example:**

```bongovromon/api.md#L937-958
{
  "success": true,
  "message": "Activity feed fetched successfully",
  "data": [
    {
      "id": "feed_1",
      "type": "activity_added",
      "message": "Rima added Ratargul Swamp Forest to Day 3",
      "created_at": "2025-06-08T14:30:00Z"
    },
    {
      "id": "feed_2",
      "type": "poll_created",
      "message": "New poll: Day 2 dinner spot?",
      "created_at": "2025-06-08T15:00:00Z"
    },
    {
      "id": "feed_3",
      "type": "vote_cast",
      "message": "Karim voted for Hotel Greenland",
      "created_at": "2025-06-08T15:12:00Z"
    }
  ]
}
```

---

# Suggested Shared Supporting APIs

These are not one of the 8 main feature pages, but they will help implementation.

## 1. Upload Media Metadata
**Endpoint:** `POST /media`

**What it does:**
Stores Cloudinary-returned media URLs and metadata after upload.

**Example Request:**

```bongovromon/api.md#L969-976
{
  "resource_type": "image",
  "url": "https://res.cloudinary.com/demo/image/upload/v1/example.jpg",
  "public_id": "example",
  "context": "community_contribution"
}
```

## 2. Search Locations
**Endpoint:** `GET /locations/search?q=sajek`

**What it does:**
Returns matching places for autocomplete fields.

**Example Response:**

```bongovromon/api.md#L984-997
{
  "success": true,
  "message": "Locations fetched successfully",
  "data": [
    {
      "id": "loc_7001",
      "name": "Sajek Valley",
      "district": "Rangamati",
      "type": "destination"
    },
    {
      "id": "loc_7002",
      "name": "Konglak Hill",
      "district": "Rangamati",
      "type": "attraction"
    }
  ]
}
```

## 3. Notification/Event API
**Endpoint:** `GET /notifications`

**What it does:**
Returns in-app notifications for alerts, collaboration, invite joins, and budget warnings.

---

# Suggested Database Entity Mapping

To support the above APIs, backend will likely need tables/entities similar to:

- `users`
- `locations`
- `community_contributions`
- `community_contribution_media`
- `group_trips`
- `group_trip_members`
- `itineraries`
- `itinerary_days`
- `itinerary_activities`
- `accommodations`
- `nomad_metric_ratings`
- `trip_budgets`
- `trip_expenses`
- `group_polls`
- `group_poll_options`
- `group_poll_votes`
- `group_activity_feed`
- `notifications`

---

# Notes for Implementation

1. **Authentication required** for create/update/delete operations.
2. **Role/ownership checks** are required for editing or deleting group trips, polls, itinerary items, and contributions.
3. **Cloudinary upload** should happen first from frontend or upload service, then backend stores returned URL.
4. **LLM-backed APIs**:
   - `/itineraries/generate`
   - `/accommodations/ai-top-pick`
   - `/itineraries/{itineraryId}/chat`
5. **Mapping/Bari Koi-backed APIs**:
   - accommodation map pin display
   - nomad map layers
6. **Real-time features** like collaborative editing, presence, poll updates, and chat streaming may additionally use **WebSocket/SSE** even if REST endpoints exist.
7. **Budget alerts** at 80% and 100% can be triggered both in-app and through notifications.
8. **Validation rules** should ensure:
   - `end_date >= start_date`
   - `price_range_max >= price_range_min`
   - valid Bangladesh location references
   - supported tags only: `Hidden Gem`, `Trending`
   - supported visibility only: `public`, `private`

---

# Final Summary

This API spec covers the 8 UI-based features grouped by member:

- **Member-1**
  - Community Data Contribution
  - Group Trip Creation

- **Member-2**
  - AI Itinerary Generation
  - Accommodation Recommendations

- **Member-3**
  - Nomad Metrics & Interactive Map
  - Live Budget Tracker

- **Member-4**
  - AI Chatbot for Itinerary Refinement
  - Collaborative Group Planning & Polling

This should be enough to start designing the backend routes, request validation, database schema planning, and frontend integration.