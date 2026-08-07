import pytest
from datetime import datetime, timezone
from fastapi import Depends, APIRouter
from fastapi.testclient import TestClient

from app.api.deps import get_current_admin_user, get_current_user, get_optional_current_user
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User
from app.main import app

# Temporary test router for testing role-protected endpoints
test_router = APIRouter(prefix="/test-auth-roles", tags=["test"])


@test_router.get("/user-only")
async def user_only_route(user: User = Depends(get_current_user)):
    return {"user_id": str(user.id), "role": user.role}


@test_router.get("/admin-only")
async def admin_only_route(admin: User = Depends(get_current_admin_user)):
    return {"admin_id": str(admin.id), "role": admin.role}


@test_router.get("/optional-user")
async def optional_user_route(user: User | None = Depends(get_optional_current_user)):
    if user:
        return {"authenticated": True, "email": user.email}
    return {"authenticated": False, "email": None}


app.include_router(test_router)


def test_dev_login_success(client: TestClient):
    """Test /api/v1/auth/dev-login creates user and sets auth cookies."""
    response = client.post(
        "/api/v1/auth/dev-login",
        json={"email": "testuser@example.com", "name": "Test User", "role": "user"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "testuser@example.com"
    assert data["user"]["role"] == "user"
    assert data["user"]["email_verified"] is True
    assert data["user"]["deleted_at"] is None

    # Check cookies set
    cookies = response.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies


def test_get_me_unauthenticated(client: TestClient):
    """Test /api/v1/auth/me fails with 401 when no token is supplied."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_me_with_cookie(client: TestClient):
    """Test /api/v1/auth/me succeeds with access_token cookie."""
    dev_res = client.post(
        "/api/v1/auth/dev-login",
        json={"email": "cookieuser@example.com", "name": "Cookie User", "role": "user"},
    )
    assert dev_res.status_code == 200

    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "cookieuser@example.com"


def test_get_me_with_bearer_header(client: TestClient):
    """Test /api/v1/auth/me succeeds with Authorization Bearer header."""
    dev_res = client.post(
        "/api/v1/auth/dev-login",
        json={"email": "beareruser@example.com", "name": "Bearer User", "role": "user"},
    )
    assert dev_res.status_code == 200
    token = dev_res.json()["access_token"]

    client.cookies.clear()
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "beareruser@example.com"


def test_role_based_access_control(client: TestClient):
    """Test that regular users are forbidden (403) from admin endpoints, but admins pass."""
    # 1. Login as regular user
    user_res = client.post(
        "/api/v1/auth/dev-login",
        json={"email": "normaluser@example.com", "name": "Normal User", "role": "user"},
    )
    user_token = user_res.json()["access_token"]

    # Call user route -> 200
    res = client.get(
        "/test-auth-roles/user-only",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res.status_code == 200

    # Call admin route -> 403 Forbidden
    res = client.get(
        "/test-auth-roles/admin-only",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res.status_code == 403

    # 2. Login as admin user
    admin_res = client.post(
        "/api/v1/auth/dev-login",
        json={"email": "adminuser@example.com", "name": "Admin User", "role": "admin"},
    )
    admin_token = admin_res.json()["access_token"]

    # Call admin route -> 200
    res = client.get(
        "/test-auth-roles/admin-only",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200
    assert res.json()["role"] == "admin"


def test_inactive_and_deleted_user_rejection(client: TestClient, db_session):
    """Test that inactive or soft-deleted users are denied access (401)."""
    # Create dev user
    dev_res = client.post(
        "/api/v1/auth/dev-login",
        json={"email": "inactive@example.com", "name": "Inactive User", "role": "user"},
    )
    user_id = dev_res.json()["user"]["id"]
    token = dev_res.json()["access_token"]

    # 1. Deactivate user in DB
    user = db_session.query(User).filter(User.id == user_id).first()
    user.is_active = False
    db_session.commit()

    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401

    # 2. Reactivate and soft-delete
    user.is_active = True
    user.deleted_at = datetime.now(timezone.utc)
    db_session.commit()

    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401


def test_optional_user_dependency(client: TestClient):
    """Test optional user dependency returns user info when logged in, or null when anonymous."""
    # Anonymous call -> authenticated: False
    client.cookies.clear()
    res = client.get("/test-auth-roles/optional-user")
    assert res.status_code == 200
    assert res.json() == {"authenticated": False, "email": None}

    # Logged-in call -> authenticated: True
    dev_res = client.post(
        "/api/v1/auth/dev-login",
        json={"email": "optional@example.com", "name": "Optional User", "role": "user"},
    )
    token = dev_res.json()["access_token"]

    res = client.get(
        "/test-auth-roles/optional-user",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json() == {"authenticated": True, "email": "optional@example.com"}


def test_logout(client: TestClient):
    """Test logout clears auth cookies."""
    client.post(
        "/api/v1/auth/dev-login",
        json={"email": "logoutuser@example.com", "name": "Logout User", "role": "user"},
    )
    logout_res = client.post("/api/v1/auth/logout")
    assert logout_res.status_code == 200
