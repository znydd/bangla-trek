import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient


def test_travel_buddy_full_workflow(client: TestClient):
    """Test full Travel Buddy public trip lifecycle, capacity lock, privacy enforcement, and email draft."""
    # 1. Organizer login & create trip (max_members = 2)
    org_res = client.post(
        "/api/v1/auth/dev-login",
        json={"email": "organizer@example.com", "name": "Organizer User", "role": "user"},
    )
    org_token = org_res.json()["access_token"]
    org_user_id = org_res.json()["user"]["id"]

    start = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    end = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

    create_res = client.post(
        "/api/v1/travel-trips",
        json={
            "title": "Sajek Valley Weekend Camping",
            "origin": "Dhaka",
            "destination": "Sajek",
            "start_at": start,
            "end_at": end,
            "meeting_point": "Kamalapur Railway Station",
            "transport": "Chander Gari",
            "estimated_cost_min_bdt": 3500.0,
            "estimated_cost_max_bdt": 6000.0,
            "description": "Camping and stargazing at Sajek.",
            "max_members": 2,
            "requirements": ["Carry NID copy", "Warm jacket"],
        },
        headers={"Authorization": f"Bearer {org_token}"},
    )
    assert create_res.status_code == 200
    trip_data = create_res.json()
    trip_id = trip_data["id"]
    assert trip_data["status"] == "scheduled"
    assert trip_data["joined_members_count"] == 1

    # 2. Public Search & Detail Check (Ensure email privacy!)
    list_res = client.get("/api/v1/travel-trips?destination=Sajek")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    detail_res = client.get(f"/api/v1/travel-trips/{trip_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["title"] == "Sajek Valley Weekend Camping"
    assert len(detail["members"]) == 1
    # Verify email field is not in public member dictionary
    assert "email" not in detail["members"][0]

    # 3. User 2 joins trip (Fills capacity 2/2 -> status becomes 'full')
    u2_res = client.post(
        "/api/v1/auth/dev-login",
        json={"email": "buddy2@example.com", "name": "Buddy Two", "role": "user"},
    )
    u2_token = u2_res.json()["access_token"]

    join_res = client.post(
        f"/api/v1/travel-trips/{trip_id}/join",
        headers={"Authorization": f"Bearer {u2_token}"},
    )
    assert join_res.status_code == 200
    assert join_res.json()["status"] == "full"
    assert join_res.json()["joined_members_count"] == 2

    # 4. User 3 attempts to join full trip -> 409 Conflict
    u3_res = client.post(
        "/api/v1/auth/dev-login",
        json={"email": "buddy3@example.com", "name": "Buddy Three", "role": "user"},
    )
    u3_token = u3_res.json()["access_token"]

    overbook_res = client.post(
        f"/api/v1/travel-trips/{trip_id}/join",
        headers={"Authorization": f"Bearer {u3_token}"},
    )
    assert overbook_res.status_code == 409

    # 5. Non-organizer attempts to access email draft -> 404/403
    unauth_draft = client.get(
        f"/api/v1/travel-trips/{trip_id}/email-draft",
        headers={"Authorization": f"Bearer {u2_token}"},
    )
    assert unauth_draft.status_code in [403, 404]

    # 6. Organizer fetches email draft -> receives BCC participant emails
    draft_res = client.get(
        f"/api/v1/travel-trips/{trip_id}/email-draft",
        headers={"Authorization": f"Bearer {org_token}"},
    )
    assert draft_res.status_code == 200
    draft_info = draft_res.json()
    assert "buddy2@example.com" in draft_info["bcc_emails"]
    assert "mailto:?bcc=" in draft_info["mailto_url"]

    # 7. User 2 leaves trip -> capacity re-opens to 'scheduled'
    leave_res = client.delete(
        f"/api/v1/travel-trips/{trip_id}/membership",
        headers={"Authorization": f"Bearer {u2_token}"},
    )
    assert leave_res.status_code == 200

    detail_reopen = client.get(f"/api/v1/travel-trips/{trip_id}")
    assert detail_reopen.json()["status"] == "scheduled"
    assert detail_reopen.json()["joined_members_count"] == 1

    # 8. Organizer cancels trip
    cancel_res = client.post(
        f"/api/v1/travel-trips/{trip_id}/cancel",
        headers={"Authorization": f"Bearer {org_token}"},
    )
    assert cancel_res.status_code == 200

    detail_cancelled = client.get(f"/api/v1/travel-trips/{trip_id}")
    assert detail_cancelled.json()["status"] == "cancelled"
