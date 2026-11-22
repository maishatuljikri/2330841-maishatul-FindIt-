
"""Integration tests for IUB Lost & Found JWT authentication and CRUD."""

from __future__ import annotations

from uuid import uuid4

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.main import app
from app.database import SessionLocal
from app.models import (
    AuthSession,
    Item,
    LoginAttempt,
    RefreshSession,
    Student,
)


@pytest.fixture
def client():
    """Create a fresh test client for each test."""
    with TestClient(app) as test_client:
        yield test_client


def make_account():
    """Create unique test account data."""

    suffix = uuid4().hex[:8]

    return {
        "student_id": f"TEST-{suffix}".upper(),
        "full_name": "CSE Test Student",
        "email": f"test-{suffix}@example.com",
        "password": "TemporaryTestPassword123!",
        "phone_number": "01712345678",
        "whatsapp_number": "01712345679",
    }


def cleanup_account(account):
    """Remove only the temporary account and its test records."""

    with SessionLocal() as db:
        student = db.scalar(
            select(Student).where(
                Student.student_id == account["student_id"]
            )
        )

        if student is not None:
            db.execute(
                delete(Item).where(Item.owner_id == student.id)
            )

            db.execute(
                delete(AuthSession).where(
                    AuthSession.student_pk == student.id
                )
            )

            db.execute(
                delete(RefreshSession).where(
                    RefreshSession.student_pk == student.id
                )
            )

            db.execute(
                delete(Student).where(Student.id == student.id)
            )

        db.execute(
            delete(LoginAttempt).where(
                LoginAttempt.identifier == account["email"]
            )
        )

        db.commit()


def register_account(client, account):
    """Register a new test student and return the response."""

    return client.post(
        "/api/auth/register",
        json=account,
    )


def bearer_headers(access_token):
    """Build an Authorization header."""

    return {
        "Authorization": f"Bearer {access_token}"
    }


def test_health_check(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_public_board_returns_items(client):
    response = client.get("/api/items")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1

    # Public visitors must not receive private contact information.
    assert response.json()[0]["contact_info"] is None


def test_signup_login_profile_refresh_and_logout(client):
    account = make_account()

    try:
        # 1. Signup.
        signup = register_account(client, account)

        assert signup.status_code == 201, signup.text

        user = signup.json()["user"]
        assert user["email"] == account["email"]
        assert user["role"] == "user"

        # Password hashes must never appear in API responses.
        assert "password_hash" not in user
        assert "password" not in user

        access_token = signup.json()["access_token"]
        assert access_token

        # Refresh token must be stored in an HTTP-only cookie.
        cookie = signup.cookies.get("iub_refresh_token")
        assert cookie

        # 2. Current authenticated user.
        profile = client.get(
            "/api/auth/me",
            headers=bearer_headers(access_token),
        )

        assert profile.status_code == 200
        assert profile.json()["email"] == account["email"]

        # 3. Wrong password must be rejected.
        wrong_login = client.post(
            "/api/auth/login",
            json={
                "email": account["email"],
                "password": "WrongPassword123!",
            },
        )

        assert wrong_login.status_code == 401

        # 4. Correct password login.
        login = client.post(
            "/api/auth/login",
            json={
                "email": account["email"],
                "password": account["password"],
            },
        )

        assert login.status_code == 200, login.text
        assert login.json()["access_token"]

        # 5. Refresh token rotation.
        refresh = client.post("/api/auth/refresh")

        assert refresh.status_code == 200, refresh.text
        assert refresh.json()["access_token"]

        # 6. Logout.
        logout = client.post("/api/auth/logout")

        assert logout.status_code == 204

        # 7. Refresh after logout must be rejected.
        refresh_after_logout = client.post("/api/auth/refresh")

        assert refresh_after_logout.status_code == 401

    finally:
        cleanup_account(account)


def test_guest_cannot_create_report(client):
    account = make_account()

    payload = {
        "title": "Guest report should be blocked",
        "description": "This report must not be created without login.",
        "category": "Other",
        "report_type": "lost",
        "location": "Library",
        "incident_date": None,
        "contact_info": "Please sign in before posting.",
    }

    # Both missing and invalid tokens must be rejected.
    for headers in (
        {},
        {"Authorization": "Bearer invalid-token"},
    ):
        response = client.post(
            "/api/items",
            headers=headers,
            json=payload,
        )

        assert response.status_code == 401

    # This test does not create a student account.
    assert account["student_id"]


def test_report_lifecycle_and_contact_privacy(client):
    owner = make_account()
    another_student = make_account()

    item_id = None

    try:
        # 1. Register the report owner.
        owner_signup = register_account(client, owner)

        assert owner_signup.status_code == 201

        owner_token = owner_signup.json()["access_token"]
        owner_headers = bearer_headers(owner_token)

        # 2. Create a report.
        created = client.post(
            "/api/items",
            headers=owner_headers,
            json={
                "title": "Test privacy item",
                "description": (
                    "This item is created for an API test."
                ),
                "category": "Other",
                "report_type": "lost",
                "location": "Test room",
                "incident_date": None,
                "contact_info": (
                    "Contact the report owner for the test."
                ),
                "image_data": "data:image/png;base64,aGVsbG8=",
            },
        )

        assert created.status_code == 201, created.text

        item_id = created.json()["id"]
        assert created.json()["is_owner"] is True

        # 3. Guest can read the report but not contact information.
        guest_response = client.get(f"/api/items/{item_id}")

        assert guest_response.status_code == 200
        assert guest_response.json()["contact_info"] is None

        # 4. Owner can view their report.
        owner_response = client.get(
            f"/api/items/{item_id}",
            headers=owner_headers,
        )

        assert owner_response.status_code == 200
        assert owner_response.json()["contact_info"] == (
            "Contact the report owner for the test."
        )

        # 5. Owner can update the report.
        updated = client.put(
            f"/api/items/{item_id}",
            headers=owner_headers,
            json={
                "title": "Test privacy item edited",
                "description": (
                    "This item was updated by its original owner."
                ),
                "category": "Other",
                "report_type": "lost",
                "location": "Updated test room",
                "incident_date": None,
                "contact_info": (
                    "Updated contact instructions for the owner."
                ),
            },
        )

        assert updated.status_code == 200
        assert updated.json()["title"] == (
            "Test privacy item edited"
        )

        # 6. Image remains available.
        photo = client.get(f"/api/items/{item_id}/image")

        assert photo.status_code == 200
        assert photo.content == b"hello"

        # 7. Public board does not expose private contact information.
        public_list = client.get(
            "/api/items",
            params={
                "q": "Test privacy item edited",
                "status": "all",
            },
        )

        assert public_list.status_code == 200

        public_item = next(
            item
            for item in public_list.json()
            if item["id"] == item_id
        )

        assert public_item["contact_info"] is None
        assert "image_data" not in public_item

        # 8. Guest cannot access private contact endpoint.
        guest_contact = client.get(
            f"/api/items/{item_id}/contact"
        )

        assert guest_contact.status_code == 401

        # 9. Owner can access contact information.
        owner_contact = client.get(
            f"/api/items/{item_id}/contact",
            headers=owner_headers,
        )

        assert owner_contact.status_code == 200
        assert owner_contact.json()["phone_number"] == (
            owner["phone_number"]
        )

        # 10. Register another student.
        other_signup = register_account(
            client,
            another_student,
        )

        assert other_signup.status_code == 201

        other_token = other_signup.json()["access_token"]
        other_headers = bearer_headers(other_token)

        # 11. Another student cannot update the owner's report.
        other_update = client.put(
            f"/api/items/{item_id}",
            headers=other_headers,
            json={
                "title": "Unauthorized edited item",
                "description": (
                    "Another student must not edit this report."
                ),
                "category": "Other",
                "report_type": "lost",
                "location": "Test room",
                "incident_date": None,
                "contact_info": "Unauthorized contact change.",
            },
        )

        assert other_update.status_code == 403

        # 12. Another student cannot resolve or delete the report.
        other_status = client.patch(
            f"/api/items/{item_id}/status",
            headers=other_headers,
            json={"status": "resolved"},
        )

        assert other_status.status_code == 403

        other_delete = client.delete(
            f"/api/items/{item_id}",
            headers=other_headers,
        )

        assert other_delete.status_code == 403

        # 13. Owner can resolve the report.
        resolved = client.patch(
            f"/api/items/{item_id}/status",
            headers=owner_headers,
            json={"status": "resolved"},
        )

        assert resolved.status_code == 200
        assert resolved.json()["status"] == "resolved"

        # 14. Owner can delete their report.
        deleted = client.delete(
            f"/api/items/{item_id}",
            headers=owner_headers,
        )

        assert deleted.status_code == 204
        item_id = None

    finally:
        cleanup_account(owner)
        cleanup_account(another_student)


def test_read_missing_item_returns_404(client):
    response = client.get("/api/items/99999999")

    assert response.status_code == 404


def test_signup_requires_valid_information(client):
    response = client.post(
        "/api/auth/register",
        json={
            "student_id": "TEST-MISSING",
            "full_name": "Missing Information",
        },
    )

    assert response.status_code == 422


def test_duplicate_signup_is_rejected(client):
    account = make_account()

    try:
        first = register_account(client, account)

        assert first.status_code == 201, first.text

        second = register_account(client, account)

        assert second.status_code == 409

    finally:
        cleanup_account(account)
