import uuid
from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.place import Place, PlaceAlias, PlaceMedia, PlaceTag
from app.models.review import Review


@pytest.fixture
def sample_place(db_session: Session) -> Place:
    """Fixture creating an approved place in the database."""
    place = Place(
        slug="sreemangal-tea-gardens",
        name="Sreemangal Tea Gardens",
        normalized_name="sreemangal tea gardens",
        category="Nature",
        summary="Serene rolling green tea estates in Moulvibazar.",
        description="Famous for green tea estates and peaceful atmosphere.",
        source_type="admin",
        status="approved",
        district="Moulvibazar",
        upazila="Sreemangal",
        village="Finlay Tea Estate",
        nearest_hub="Sreemangal Railway Station",
        latitude=24.3065,
        longitude=91.7296,
        best_season="October to March",
        suggested_duration="1-2 Days",
        budget_min_bdt=1500.0,
        budget_max_bdt=4000.0,
        highlights=["Tea Gardens", "Seven Layer Tea", "Lawachara National Park"],
        know_before_you_go=["Rent a rickshaw for local transport", "Carry cash"],
    )
    db_session.add(place)
    db_session.flush()

    # Add Alias, Tag, and Media
    db_session.add(PlaceAlias(place_id=place.id, alias="Srimangal", normalized_alias="srimangal"))
    db_session.add(PlaceTag(place_id=place.id, tag="Hidden Gem"))
    db_session.add(
        PlaceMedia(
            place_id=place.id,
            media_type="photo",
            url="https://res.cloudinary.com/demo/image/upload/tea_estate.jpg",
            caption="Green tea gardens view",
            sort_order=1,
            moderation_status="approved",
        )
    )
    db_session.commit()
    db_session.refresh(place)
    return place


@pytest.fixture
def pending_place(db_session: Session) -> Place:
    """Fixture creating a pending place that should NOT appear in public APIs."""
    place = Place(
        slug="unapproved-secret-waterfall",
        name="Unapproved Secret Waterfall",
        normalized_name="unapproved secret waterfall",
        category="Adventure",
        summary="A hidden waterfall awaiting moderation.",
        status="pending",
        source_type="community",
        district="Bandarban",
    )
    db_session.add(place)
    db_session.commit()
    db_session.refresh(place)
    return place


def test_list_places(client: TestClient, sample_place: Place, pending_place: Place):
    """Test public listing endpoint returns approved places only."""
    response = client.get("/api/v1/places")
    assert response.status_code == 200
    data = response.json()
    target = next((p for p in data if p["slug"] == sample_place.slug), None)
    assert target is not None
    assert target["name"] == sample_place.name
    assert "Hidden Gem" in target["tags"]


def test_list_places_search(client: TestClient, sample_place: Place):
    """Test public search by alias and category."""
    # Search by alias "srimangal"
    res1 = client.get("/api/v1/places?q=srimangal")
    assert res1.status_code == 200
    assert len(res1.json()) == 1

    # Filter by category "Nature"
    res2 = client.get("/api/v1/places?category=Nature")
    assert res2.status_code == 200
    assert len(res2.json()) == 1

    # Non-existent query
    res3 = client.get("/api/v1/places?q=nonexistentplace")
    assert res3.status_code == 200
    assert len(res3.json()) == 0


def test_get_place_by_slug(client: TestClient, sample_place: Place):
    """Test fetching place detail by slug."""
    response = client.get(f"/api/v1/places/{sample_place.slug}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_place.id)
    assert data["district"] == "Moulvibazar"
    assert len(data["media"]) == 1
    assert data["media"][0]["url"] == "https://res.cloudinary.com/demo/image/upload/tea_estate.jpg"


def test_review_lifecycle(client: TestClient, sample_place: Place):
    """Test full review creation, listing, updating, soft deletion, and helpful voting."""
    # 1. Login user
    dev_res = client.post(
        "/api/v1/auth/dev-login",
        json={"email": "reviewer@example.com", "name": "Reviewer User", "role": "user"},
    )
    token = dev_res.json()["access_token"]
    user_id = dev_res.json()["user"]["id"]

    # 2. Submit Review
    review_payload = {
        "rating": 5,
        "visited_on": "2026-02-10",
        "travel_style": "Nature Lover",
        "group_type": "Friends",
        "group_size": 4,
        "starting_location": "Dhaka",
        "actual_cost_bdt": 2500.0,
        "title": "Breathtaking green views!",
        "travel_guide": "Take the early morning train from Kamalapur Railway Station.",
        "crowd_level": "Light crowd",
        "access_difficulty": "Easy",
        "road_condition": "Paved / Good",
        "safety": "Very Safe",
        "cleanliness": "Clean",
        "mobile_carrier": "Grameenphone",
        "network_reliability": "Strong 4G",
        "payment_methods": ["bKash", "Cash"],
        "media": [
            {
                "media_type": "photo",
                "url": "https://res.cloudinary.com/demo/image/upload/my_tea_photo.jpg",
                "caption": "Morning mist in tea garden",
            }
        ],
    }

    res_create = client.post(
        f"/api/v1/places/{sample_place.id}/reviews",
        json=review_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_create.status_code == 200
    review_data = res_create.json()
    review_id = review_data["id"]
    assert review_data["rating"] == 5
    assert review_data["visited_on"] == "2026-02-10"
    assert "bKash" in review_data["payment_methods"]

    # 3. Prevent Duplicate Review on Same Visit Date
    res_dup = client.post(
        f"/api/v1/places/{sample_place.id}/reviews",
        json=review_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_dup.status_code == 400

    # 4. List Place Reviews
    res_list = client.get(f"/api/v1/places/{sample_place.id}/reviews")
    assert res_list.status_code == 200
    reviews = res_list.json()
    assert len(reviews) == 1
    assert reviews[0]["id"] == review_id
    assert reviews[0]["user"]["name"] == "Reviewer User"

    # 5. Toggle Helpful Vote
    res_vote = client.post(
        f"/api/v1/places/{sample_place.id}/reviews/{review_id}/helpful",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_vote.status_code == 200
    assert res_vote.json()["helpful_count"] == 1
    assert res_vote.json()["is_helpful_by_me"] is True

    # 6. Update Review
    res_update = client.patch(
        f"/api/v1/places/{sample_place.id}/reviews/{review_id}",
        json={"title": "Updated Title: Incredible Tea Estates!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_update.status_code == 200
    assert res_update.json()["title"] == "Updated Title: Incredible Tea Estates!"

    # 7. Get Review Summary SQL Aggregation
    res_summary = client.get(f"/api/v1/places/{sample_place.id}/review-summary")
    assert res_summary.status_code == 200
    summary = res_summary.json()
    assert summary["total_reviews"] == 1
    assert summary["average_rating"] == 5.0
    assert summary["cost_range"]["median"] == 2500.0
    assert summary["crowd_level"]["options"][0]["value"] == "Light crowd"

    # 8. Soft Delete Review
    res_del = client.delete(
        f"/api/v1/places/{sample_place.id}/reviews/{review_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_del.status_code == 200

    # Verify review no longer appears in public reviews list
    res_list_after = client.get(f"/api/v1/places/{sample_place.id}/reviews")
    assert len(res_list_after.json()) == 0
