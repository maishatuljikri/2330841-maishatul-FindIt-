
"""Password hashing and JWT security utilities."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash


# Load secrets from backend/.env during local development.
BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env", override=False)


# Security configuration.
JWT_ALGORITHM = "HS256"
JWT_ISSUER = "iub-lost-and-found"
JWT_AUDIENCE = "iub-lost-and-found-api"
ACCESS_TOKEN_MINUTES = 15

password_hasher = PasswordHash.recommended()


def get_secret(name: str) -> str:
    """Read a required secret from environment variables."""

    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Environment variable {name} is missing."
        )

    if len(value) < 32:
        raise RuntimeError(
            f"{name} must contain at least 32 characters."
        )

    return value


def prepare_password(password: str) -> str:
    """Combine the password with a server-side pepper."""

    if not isinstance(password, str) or not password:
        raise ValueError("Password cannot be empty.")

    pepper = get_secret("PASSWORD_PEPPER")

    return hmac.new(
        pepper.encode("utf-8"),
        password.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def hash_password(password: str) -> str:
    """Create an Argon2 password hash."""

    prepared = prepare_password(password)
    return password_hasher.hash(prepared)


def verify_password(password: str, stored_hash: str) -> bool:
    """Check whether a password matches its stored hash."""

    if not stored_hash:
        return False

    try:
        prepared = prepare_password(password)
        return password_hasher.verify(prepared, stored_hash)
    except (ValueError, TypeError):
        return False


def create_access_token(
    user_id: int,
    role: str,
) -> str:
    """Create a JWT access token valid for 15 minutes."""

    if user_id <= 0:
        raise ValueError("Invalid user ID.")

    if role not in {"user", "admin"}:
        raise ValueError("Invalid user role.")

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "role": role,
        "token_type": "access",
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_MINUTES),
        "jti": secrets.token_urlsafe(16),
    }

    return jwt.encode(
        payload,
        get_secret("JWT_SECRET_KEY"),
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """Verify a JWT and return its payload."""

    payload = jwt.decode(
        token,
        get_secret("JWT_SECRET_KEY"),
        algorithms=[JWT_ALGORITHM],
        issuer=JWT_ISSUER,
        audience=JWT_AUDIENCE,
        options={
            "require": [
                "sub",
                "role",
                "token_type",
                "iss",
                "aud",
                "iat",
                "exp",
                "jti",
            ]
        },
    )

    if payload.get("token_type") != "access":
        raise jwt.InvalidTokenError("Invalid token type.")

    if payload.get("role") not in {"user", "admin"}:
        raise jwt.InvalidTokenError("Invalid token role.")

    issued_at = payload["iat"]
    expires_at = payload["exp"]

    if expires_at <= issued_at:
        raise jwt.InvalidTokenError("Invalid token lifetime.")

    if expires_at - issued_at > ACCESS_TOKEN_MINUTES * 60:
        raise jwt.InvalidTokenError("Access token lifetime is too long.")

    return payload
