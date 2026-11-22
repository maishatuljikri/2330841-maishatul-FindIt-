
"""Automated tests for student profile and password management."""

from __future__ import annotations

from uuid import uuid4

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.main import app
from app.database import SessionLocal
from app.models import AuthSession, Item, LoginAttempt, RefreshSession, Student


@pytest.fixture
def client():
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


def make_account():
    """Generate unique test account data."""
    suffix = uuid4().hex[:8]

    return {
        "student_id": f"PROFILE-{suffix}".upper(),
        "full_name": "Profile Test Student",
        "email": f"profile-{suffix}@example.com",
        "password": "TemporaryPassword123!",
        "phone_number": "01712345678",
        "whatsapp_number": "01812345678",
        "extra_contact_info": "Available after 3 PM",
    }


def cleanup_account(account):
    """Delete only the temporary test account and its records."""
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
            db.delete(student)

        db.execute(
            delete(LoginAttempt).where(
                LoginAttempt.identifier == account["email"]
            )
        )
        db.commit()


def register_test_student(client, account):
    """Register a temporary student account."""
    return client.post(
        "/api/auth/register",
        json=account,
    )


def auth_headers(token):
    """Create a Bearer Authorization header."""
    return {"Authorization": f"Bearer {token}"}


def test_profile_requires_authentication(client):
    """Guests cannot access private profile information."""

    response = client.get("/api/auth/profile")

    assert response.status_code == 401


def test_student_can_view_and_update_own_profile(client):
    """A student can view and update their own profile."""

    account = make_account()

    try:
        signup = register_test_student(client, account)
        assert signup.status_code == 201, signup.text

        token = signup.json()["access_token"]
        headers = auth_headers(token)

        # Read the profile.
        profile = client.get(
            "/api/auth/profile",
            headers=headers,
        )

        assert profile.status_code == 200
        assert profile.json()["student_id"] == account["student_id"]
        assert profile.json()["email"] == account["email"]

        # Update profile information.
        update = client.patch(
            "/api/auth/profile",
            headers=headers,
            json={
                "full_name": "Updated Profile Student",
                "phone_number": "01912345678",
                "whatsapp_number": "01612345678",
                "extra_contact_info": "Available after 5 PM",
            },
        )

        assert update.status_code == 200, update.text
        assert update.json()["full_name"] == "Updated Profile Student"
        assert update.json()["phone_number"] == "01912345678"
        assert update.json()["whatsapp_number"] == "01612345678"
        assert update.json()["extra_contact_info"] == "Available after 5 PM"

        # Confirm that changes were saved.
        refreshed_profile = client.get(
            "/api/auth/profile",
            headers=headers,
        )

        assert refreshed_profile.status_code == 200
        assert refreshed_profile.json()["full_name"] == (
            "Updated Profile Student"
        )

        # A user must not change protected fields such as role or email.
        forbidden_update = client.patch(
            "/api/auth/profile",
            headers=headers,
            json={"role": "admin", "email": "admin@example.com"},
        )

        assert forbidden_update.status_code == 422

    finally:
        cleanup_account(account)


def test_student_can_change_password_and_revoke_refresh_sessions(client):
    """A student can change their password and revoke refresh sessions."""

    account = make_account()
    new_password = "NewSecurePassword456!"

    try:
        signup = register_test_student(client, account)
        assert signup.status_code == 201, signup.text

        token = signup.json()["access_token"]
        headers = auth_headers(token)

        # An incorrect current password must be rejected.
        wrong_password = client.post(
            "/api/auth/change-password",
            headers=headers,
            json={
                "current_password": "IncorrectPassword123!",
                "new_password": new_password,
            },
        )

        assert wrong_password.status_code == 400

        # The original refresh session should still work
        # after a rejected password-change attempt.
        refresh = client.post("/api/auth/refresh")

        assert refresh.status_code == 200, refresh.text

        refreshed_token = refresh.json()["access_token"]
        refreshed_headers = auth_headers(refreshed_token)

        # Change password using the correct current password.
        changed = client.post(
            "/api/auth/change-password",
            headers=refreshed_headers,
            json={
                "current_password": account["password"],
                "new_password": new_password,
            },
        )

        assert changed.status_code == 204

        # Refresh session must be revoked after password change.
        refresh_after_change = client.post("/api/auth/refresh")

        assert refresh_after_change.status_code == 401

        # The old password must no longer work.
        old_login = client.post(
            "/api/auth/login",
            json={
                "email": account["email"],
                "password": account["password"],
            },
        )

        assert old_login.status_code == 401

        # The new password must work.
        new_login = client.post(
            "/api/auth/login",
            json={
                "email": account["email"],
                "password": new_password,
            },
        )

        assert new_login.status_code == 200, new_login.text
        assert new_login.json()["access_token"]

    finally:
        cleanup_account(account)
