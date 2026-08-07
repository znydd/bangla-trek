import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.place import Place
from app.models.user import User
from app.services.ai_service import AIService



@pytest.fixture
def approved_place(db_session: Session) -> Place:
    """Fixture creating an approved place for AI context tests."""
    place = Place(
        slug="bandarban-nilgiri",
        name="Nilgiri Resort Bandarban",
        normalized_name="bandarban-nilgiri",
        category="Hill Station",
        summary="High altitude resort in Bandarban surrounded by clouds.",
        status="approved",
        district="Bandarban",
        upazila="Thanchi",
        budget_min_bdt=3000.0,
        budget_max_bdt=8000.0,
        highlights=["Cloud views", "Chimbuk Hill", "Peak altitude"],
    )
    db_session.add(place)
    db_session.commit()
    db_session.refresh(place)
    return place


def test_ai_conversation_lifecycle(client: TestClient, approved_place: Place):
    """Test full AI conversation creation, place context pinning, SSE streaming, and deletion."""
    # 1. Login user
    dev_res = client.post(
        "/api/v1/auth/dev-login",
        json={"email": "aistudent@example.com", "name": "AI Student", "role": "user"},
    )
    token = dev_res.json()["access_token"]

    # 2. Create conversation
    create_res = client.post(
        "/api/v1/ai/conversations",
        json={"title": "Bandarban Trip Planning"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_res.status_code == 200
    conv_data = create_res.json()
    conv_id = conv_data["id"]
    assert conv_data["title"] == "Bandarban Trip Planning"

    # 3. List conversations
    list_res = client.get(
        "/api/v1/ai/conversations",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # 4. Pin place to conversation context card
    pin_res = client.put(
        f"/api/v1/ai/conversations/{conv_id}/places/{approved_place.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert pin_res.status_code == 200
    detail_data = pin_res.json()
    assert len(detail_data["context_places"]) == 1
    assert detail_data["context_places"][0]["place_id"] == str(approved_place.id)

    # 5. Send Message & Stream SSE
    msg_res = client.post(
        f"/api/v1/ai/conversations/{conv_id}/messages",
        json={"content": "What is the best itinerary for visiting Nilgiri?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert msg_res.status_code == 200
    assert "text/event-stream" in msg_res.headers["content-type"]
    sse_body = msg_res.text
    assert "data: " in sse_body
    assert "[DONE]" in sse_body

    # 6. Verify messages saved in conversation history
    detail_res = client.get(
        f"/api/v1/ai/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail_res.status_code == 200
    msgs = detail_res.json()["messages"]
    assert len(msgs) == 2  # user + assistant
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"

    # 7. Unpin place from context
    unpin_res = client.delete(
        f"/api/v1/ai/conversations/{conv_id}/places/{approved_place.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert unpin_res.status_code == 200
    assert len(unpin_res.json()["context_places"]) == 0

    # 8. Delete conversation
    del_res = client.delete(
        f"/api/v1/ai/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert del_res.status_code == 200


def test_ai_context_document_generation(db_session: Session, approved_place: Place):
    """Test AIService context document builder formatting and prompt-injection escaping."""
    user = User(
        google_id="test_ai_user_google_id",
        email="ai_test_user@example.com",
        name="AI Test User",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    ai_svc = AIService(db_session)
    conv_read = ai_svc.create_conversation(user_id=user.id, title="Test Context")
    conv_id = conv_read.id

    ai_svc.add_place_to_context(
        conversation_id=conv_id, user_id=user.id, place_id=approved_place.id
    )

    doc = ai_svc.build_place_context_document(conv_id)
    assert "Nilgiri Resort Bandarban" in doc
    assert "Bandarban" in doc
    assert "<user_reviews_data>" in doc
    assert "IMPORTANT INSTRUCTIONS FOR MODEL" in doc

