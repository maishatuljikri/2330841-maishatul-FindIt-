
"""Reusable authentication and authorization dependencies."""

from __future__ import annotations

from collections.abc import Callable

import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import Student
from .security import decode_access_token


# Read Bearer tokens from the Authorization header.
bearer_scheme = HTTPBearer(auto_error=False)


def get_jwt_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> Student:
    """
    Verify the JWT and return the authenticated student.

    Also checks whether the account is banned and whether
    the role in the token matches the current database role.
    """

    # 1. Check whether the request contains a Bearer token.
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Verify the token signature and claims.
    try:
        payload = decode_access_token(credentials.credentials)

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    # 3. Extract the user ID from the JWT subject.
    subject = payload.get("sub")

    try:
        user_id = int(subject)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identity in access token.",
        ) from None

    # 4. Load the current account from the database.
    student = db.get(Student, user_id)

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found.",
        )

    # 5. Reject banned accounts.
    if student.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been suspended.",
        )

    # 6. Check whether the role has changed since token creation.
    if payload.get("role") != student.role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your access token is outdated. Please sign in again.",
        )

    return student


def require_roles(*allowed_roles: str) -> Callable:
    """
    Create a reusable role-based authorization dependency.

    Example:
        Depends(require_roles("admin"))
    """

    valid_roles = {"user", "admin"}

    if not allowed_roles:
        raise ValueError("At least one role must be specified.")

    if any(role not in valid_roles for role in allowed_roles):
        raise ValueError("An unsupported role was specified.")

    def check_role(
        current_user: Student = Depends(get_jwt_current_user),
    ) -> Student:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )

        return current_user

    return check_role

def get_optional_jwt_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> Student | None:
    """
    Return the authenticated student if a valid JWT is provided.

    Guests can still browse public Lost & Found reports.
    Invalid supplied tokens are rejected.
    """

    # No Authorization header: treat the visitor as a guest.
    if credentials is None:
        return None

    # Verify the provided JWT.
    try:
        payload = decode_access_token(credentials.credentials)

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    # Extract the account ID.
    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identity.",
        ) from None

    # Retrieve the account from the database.
    student = db.get(Student, user_id)

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found.",
        )

    # Reject suspended accounts.
    if student.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been suspended.",
        )

    # Ensure the JWT role matches the current database role.
    if payload.get("role") != student.role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your access token is outdated.",
        )

    return student
