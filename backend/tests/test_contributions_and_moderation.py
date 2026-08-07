import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.place import Place, PlaceAlias


def test_duplicate_check(client: TestClient, db_session: Session):
    """Test duplicate check matches existing place name or alias."""
    # Create an approved place
    place = Place(
        slug="jaflong-stone-river",
        name="Jaflong Stone River",
        normalized_name="jaflong-stone-river",
        category="Nature",
        summary="Scenic stone collection river in Sylhet.",
        status="approved",
        district="Sylhet",
    )
    db_session.add(place)
    db_session.flush()
    db_session.add(PlaceAlias(place_id=place.id, alias="Ziaflong", normalized_alias="ziaflong"))
    db_session.commit()

    # Exact name check
    res_exact = client.get("/api/v1/places/duplicate-check?name=Jaflong%20Stone%20River")
    assert res_exact.status_code == 200
    data_exact = res_exact.json()
    assert data_exact["has_exact_match"] is True
    assert len(data_exact["matches"]) == 1

    # Alias check
    res_alias = client.get("/api/v1/places/duplicate-check?name=Ziaflong")
    assert res_alias.status_code == 200
    assert len(res_alias.json()["matches"]) == 1

    # Unique check
    res_clean = client.get("/api/v1/places/duplicate-check?name=NonExistentWaterfall")
    assert res_clean.status_code == 200
    assert res_clean.json()["has_exact_match"] is False
    assert len(res_clean.json()["matches"]) == 0


def test_contribution_draft_to_approval_flow(client: TestClient):
    """Test user creating draft -> submitting -> admin approval -> public availability."""
    # 1. User login & create draft
    user_res = client.post(
        "/api/v1/auth/dev-login",
        json={"email": "contributor@example.com", "name": "Contributor User", "role": "user"},
    )
    user_token = user_res.json()["access_token"]

    draft_res = client.post(
        "/api/v1/places/drafts",
        json={
            "name": "Bichanakandi River",
            "category": "Nature",
            "summary": "Beautiful riverbed with rocks.",
            "district": "Sylhet",
            "upazila": "Gowainghat",
            "tags": ["River", "Hidden Gem"],
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert draft_res.status_code == 200
    draft_data = draft_res.json()
    place_id = draft_data["id"]
    assert draft_data["status"] == "draft"

    # 2. Submit draft with initial review
    submit_res = client.post(
        f"/api/v1/places/drafts/{place_id}/submit",
        json={
            "initial_review": {
                "rating": 5,
                "visited_on": "2026-03-01",
                "travel_guide": "Hire a boat from Gowainghat.",
                "crowd_level": "Moderate",
            }
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert submit_res.status_code == 200
    assert submit_res.json()["status"] == "pending"

    # Pending place must NOT be public yet
    pub_res = client.get("/api/v1/places")
    assert not any(p["id"] == place_id for p in pub_res.json())

    # 3. User trying admin approval -> 403 Forbidden
    unauth_admin = client.post(
        f"/api/v1/admin/place-submissions/{place_id}/approve",
        json={"notes": "Self approval test"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert unauth_admin.status_code == 403

    # 4. Admin login & inspect queue
    admin_res = client.post(
        "/api/v1/auth/dev-login",
        json={"email": "adminmod@example.com", "name": "Admin Mod", "role": "admin"},
    )
    admin_token = admin_res.json()["access_token"]

    queue_res = client.get(
        "/api/v1/admin/place-submissions",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert queue_res.status_code == 200
    pending_items = queue_res.json()
    assert any(item["place"]["id"] == place_id for item in pending_items)

    # 5. Admin Approve
    approve_res = client.post(
        f"/api/v1/admin/place-submissions/{place_id}/approve",
        json={"notes": "Verified location & details."},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "approved"

    # 6. Place is now public with initial review
    pub_res_after = client.get("/api/v1/places")
    assert any(p["id"] == place_id for p in pub_res_after.json())

    reviews_res = client.get(f"/api/v1/places/{place_id}/reviews")
    assert reviews_res.status_code == 200
    assert len(reviews_res.json()) == 1
    assert reviews_res.json()[0]["rating"] == 5

    # 7. Verify Audit Log
    logs_res = client.get(
        "/api/v1/admin/moderation-logs",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert logs_res.status_code == 200
    logs = logs_res.json()
    assert any(log["entity_id"] == place_id and log["action"] == "approved" for log in logs)


def test_contribution_merge_flow(client: TestClient, db_session: Session):
    """Test admin merging a duplicate submission into an existing canonical place."""
    # Canonical place
    canonical = Place(
        slug="saint-martins-island",
        name="Saint Martin's Island",
        normalized_name="saint-martins-island",
        category="Island",
        summary="Only coral island in Bangladesh.",
        status="approved",
        district="Cox's Bazar",
    )
    db_session.add(canonical)
    db_session.commit()
    canonical_id = str(canonical.id)

    # Contributor submits duplicate place
    user_res = client.post(
        "/api/v1/auth/dev-login",
        json={"email": "user2@example.com", "name": "User Two", "role": "user"},
    )
    user_token = user_res.json()["access_token"]

    draft_res = client.post(
        "/api/v1/places/drafts",
        json={
            "name": "St Martins Coral Beach",
            "category": "Island",
            "summary": "Coral beach area.",
            "district": "Cox's Bazar",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    dup_place_id = draft_res.json()["id"]

    client.post(
        f"/api/v1/places/drafts/{dup_place_id}/submit",
        json={
            "initial_review": {
                "rating": 4,
                "visited_on": "2026-01-15",
                "travel_guide": "Crystal clear water!",
            }
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Admin merge
    admin_res = client.post(
        "/api/v1/auth/dev-login",
        json={"email": "admin@example.com", "name": "Admin", "role": "admin"},
    )
    admin_token = admin_res.json()["access_token"]

    merge_res = client.post(
        f"/api/v1/admin/place-submissions/{dup_place_id}/merge",
        json={
            "target_canonical_place_id": canonical_id,
            "reason": "Duplicate of canonical Saint Martin's Island place.",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert merge_res.status_code == 200
    assert merge_res.json()["status"] == "merged"

    # Verify initial review was re-attributed to canonical place
    reviews_res = client.get(f"/api/v1/places/{canonical_id}/reviews")
    assert reviews_res.status_code == 200
    assert len(reviews_res.json()) == 1
    assert reviews_res.json()[0]["rating"] == 4
