
"""Authentication API routes for IUB Lost & Found."""

from __future__ import annotations

import hashlib
import os
import secrets
import uuid

from datetime import datetime, timedelta, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from sqlalchemy import func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_jwt_current_user
from ..models import LoginAttempt, RefreshSession, Student
from ..schemas import (
    AuthTokenResponse,
    AuthUserPublic,
    PasswordChangeRequest,
    PasswordLoginRequest,
    ProfileUpdateRequest,
    SignupRequest,
)
from ..security import (
    create_access_token,
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"],
)

REFRESH_TOKEN_DAYS = 7
REFRESH_COOKIE_NAME = "iub_refresh_token"


def _utcnow() -> datetime:
    """Return UTC time as a naive datetime for SQLAlchemy DateTime columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _hash_refresh_token(token: str) -> str:
    """Store only a SHA-256 hash of the refresh token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _get_cookie_settings() -> dict:
    """Return secure cookie settings for local and production environments."""

    is_production = bool(
        os.getenv("VERCEL") or os.getenv("VERCEL_ENV")
    )

    secure_default = "true" if is_production else "false"

    secure = os.getenv(
        "REFRESH_COOKIE_SECURE",
        secure_default,
    ).lower() in {"1", "true", "yes"}

    same_site = os.getenv(
        "REFRESH_COOKIE_SAMESITE",
        "lax",
    ).lower()

    if same_site not in {"lax", "strict", "none"}:
        raise RuntimeError("Invalid REFRESH_COOKIE_SAMESITE setting.")

    if same_site == "none" and not secure:
        raise RuntimeError(
            "SameSite=None requires a Secure refresh cookie."
        )

    return {
        "httponly": True,
        "secure": secure,
        "samesite": same_site,
        "path": "/api/auth",
    }


def _set_refresh_cookie(response: Response, token: str) -> None:
    """Send the refresh token through an HTTP-only cookie."""

    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        max_age=REFRESH_TOKEN_DAYS * 24 * 60 * 60,
        **_get_cookie_settings(),
    )


def _clear_refresh_cookie(response: Response) -> None:
    """Remove the refresh cookie using the same cookie settings."""

    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        **_get_cookie_settings(),
    )


def _client_ip(request: Request) -> str | None:
    """Get the client address reported by the ASGI server."""

    if request.client is None:
        return None

    return request.client.host[:45]


def _record_login_attempt(
    db: Session,
    request: Request,
    identifier: str,
    successful: bool,
    failure_reason: str | None = None,
) -> None:
    """Save an authentication attempt for security monitoring."""

    user_agent = request.headers.get("user-agent")

    db.add(
        LoginAttempt(
            identifier=identifier[:255],
            ip_address=_client_ip(request),
            user_agent=user_agent[:500] if user_agent else None,
            successful=successful,
            failure_reason=failure_reason,
        )
    )


def _create_refresh_session(
    db: Session,
    student: Student,
    request: Request,
    family_id: str | None = None,
) -> str:
    """Create a refresh token and store only its hash."""

    raw_token = secrets.token_urlsafe(48)

    record = RefreshSession(
        token_hash=_hash_refresh_token(raw_token),
        student_pk=student.id,
        family_id=family_id or str(uuid.uuid4()),
        expires_at=_utcnow() + timedelta(days=REFRESH_TOKEN_DAYS),
        ip_address=_client_ip(request),
        user_agent=(
            request.headers.get("user-agent", "")[:500] or None
        ),
    )

    db.add(record)

    return raw_token


def _token_response(student: Student) -> AuthTokenResponse:
    """Build a response containing a short-lived access token."""

    access_token = create_access_token(
        user_id=student.id,
        role=student.role,
    )

    return AuthTokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=15 * 60,
        user=AuthUserPublic.model_validate(student),
    )


def _record_failed_login(
    db: Session,
    request: Request,
    email: str,
    reason: str,
) -> None:
    """Record a failed login before returning an error."""

    _record_login_attempt(
        db=db,
        request=request,
        identifier=email,
        successful=False,
        failure_reason=reason,
    )

    db.commit()


@router.post(
    "/register",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: SignupRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> AuthTokenResponse:
    """Create a new student account."""

    existing = db.scalar(
        select(Student).where(
            or_(
                Student.student_id == payload.student_id,
                func.lower(Student.email) == payload.email,
            )
        )
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student ID or email is already registered.",
        )

    # Do not allow public signup to claim an existing legacy demo profile.
    # A separate verified account-claim process can be added later.
    

    student = Student(
        student_id=payload.student_id,
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role="user",
        is_banned=False,
        phone_number=payload.phone_number,
        whatsapp_number=payload.whatsapp_number,
        extra_contact_info=payload.extra_contact_info,
        password_changed_at=_utcnow(),
    )

    try:
        db.add(student)
        db.flush()

        refresh_token = _create_refresh_session(
            db=db,
            student=student,
            request=request,
        )

        _record_login_attempt(
            db=db,
            request=request,
            identifier=payload.email,
            successful=True,
        )

        db.commit()
        db.refresh(student)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student ID or email is already registered.",
        ) from None

    _set_refresh_cookie(response, refresh_token)

    return _token_response(student)



@router.post(
    "/login",
    response_model=AuthTokenResponse,
)
def login(
    payload: PasswordLoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> AuthTokenResponse:
    """Authenticate a student using email and password."""

    student = db.scalar(
        select(Student).where(
            func.lower(Student.email) == payload.email
        )
    )

    # Return the same message for unknown accounts and incorrect passwords.
    if (
        student is None
        or not student.password_hash
        or not verify_password(
            payload.password,
            student.password_hash,
        )
    ):
        _record_failed_login(
            db,
            request,
            payload.email,
            "invalid_credentials",
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if student.is_banned:
        _record_failed_login(
            db,
            request,
            payload.email,
            "account_banned",
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been suspended.",
        )

    student.last_login_at = _utcnow()

    refresh_token = _create_refresh_session(
        db=db,
        student=student,
        request=request,
    )

    _record_login_attempt(
        db=db,
        request=request,
        identifier=payload.email,
        successful=True,
    )

    db.commit()
    db.refresh(student)

    _set_refresh_cookie(response, refresh_token)

    return _token_response(student)


@router.post(
    "/refresh",
    response_model=AuthTokenResponse,
)
def refresh_access_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> AuthTokenResponse:
    """Rotate a refresh token and issue a new access token."""

    raw_token = request.cookies.get(REFRESH_COOKIE_NAME)

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session is missing.",
        )

    old_hash = _hash_refresh_token(raw_token)

    old_session = db.scalar(
        select(RefreshSession).where(
            RefreshSession.token_hash == old_hash
        )
    )

    if old_session is None:
        _clear_refresh_cookie(response)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh session.",
        )

    now = _utcnow()

    # Reuse of a previously rotated token revokes its entire session family.
    if old_session.revoked_at is not None:
        db.execute(
            update(RefreshSession)
            .where(
                RefreshSession.family_id == old_session.family_id,
                RefreshSession.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )

        db.commit()
        _clear_refresh_cookie(response)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token reuse detected. Please sign in again.",
        )

    if old_session.expires_at <= now:
        old_session.revoked_at = now
        db.commit()
        _clear_refresh_cookie(response)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session has expired.",
        )

    student = db.get(Student, old_session.student_pk)

    if student is None:
        old_session.revoked_at = now
        db.commit()
        _clear_refresh_cookie(response)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found.",
        )

    if student.is_banned:
        db.execute(
            update(RefreshSession)
            .where(
                RefreshSession.family_id == old_session.family_id,
                RefreshSession.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )

        db.commit()
        _clear_refresh_cookie(response)

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been suspended.",
        )

    # Rotate the refresh token. The previous token becomes unusable.
    new_token = secrets.token_urlsafe(48)
    new_hash = _hash_refresh_token(new_token)

    old_session.revoked_at = now
    old_session.replaced_by_token_hash = new_hash

    new_session = RefreshSession(
        token_hash=new_hash,
        student_pk=student.id,
        family_id=old_session.family_id,
        expires_at=now + timedelta(days=REFRESH_TOKEN_DAYS),
        ip_address=_client_ip(request),
        user_agent=request.headers.get("user-agent", "")[:500] or None,
    )

    db.add(new_session)
    db.commit()
    db.refresh(student)

    _set_refresh_cookie(response, new_token)

    return _token_response(student)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> Response:
    """Revoke the current refresh-token family and clear its cookie."""

    raw_token = request.cookies.get(REFRESH_COOKIE_NAME)

    if raw_token:
        token_hash = _hash_refresh_token(raw_token)

        session_record = db.scalar(
            select(RefreshSession).where(
                RefreshSession.token_hash == token_hash
            )
        )

        if session_record is not None:
            db.execute(
                update(RefreshSession)
                .where(
                    RefreshSession.family_id == session_record.family_id,
                    RefreshSession.revoked_at.is_(None),
                )
                .values(revoked_at=_utcnow())
            )

            db.commit()

    _clear_refresh_cookie(response)

    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get(
    "/me",
    response_model=AuthUserPublic,
)
def current_account(
    current_user: Student = Depends(get_jwt_current_user),
) -> Student:
    """Return the currently authenticated account."""

    return current_user


# =====================================================
# STUDENT PROFILE MANAGEMENT
# =====================================================

@router.get(
    "/profile",
    response_model=AuthUserPublic,
)
def get_profile(
    current_user: Student = Depends(get_jwt_current_user),
) -> Student:
    """Return the profile of the currently authenticated student."""

    return current_user


@router.patch(
    "/profile",
    response_model=AuthUserPublic,
)
def update_profile(
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_jwt_current_user),
) -> Student:
    """Update only the authenticated student's own profile."""

    changes = payload.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide at least one profile field to update.",
        )

    allowed_fields = {
        "full_name",
        "phone_number",
        "whatsapp_number",
        "extra_contact_info",
    }

    for field, value in changes.items():
        if field not in allowed_fields:
            continue

        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user


# =====================================================
# PASSWORD CHANGE
# =====================================================

@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def change_password(
    payload: PasswordChangeRequest,
    response: Response,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_jwt_current_user),
) -> Response:
    """Change the current password and revoke all refresh sessions."""

    if not current_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account does not have a password yet.",
        )

    # Verify the current password before allowing a change.
    if not verify_password(
        payload.current_password,
        current_user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    # Do not allow the existing password to be reused.
    if verify_password(
        payload.new_password,
        current_user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The new password must be different.",
        )

    # Save the new Argon2 password hash.
    current_user.password_hash = hash_password(
        payload.new_password
    )
    current_user.password_changed_at = _utcnow()

    # Revoke every active refresh session for this student.
    db.execute(
        update(RefreshSession)
        .where(
            RefreshSession.student_pk == current_user.id,
            RefreshSession.revoked_at.is_(None),
        )
        .values(revoked_at=_utcnow())
    )

    db.commit()

    # Remove the refresh cookie from this browser.
    _clear_refresh_cookie(response)

    response.status_code = status.HTTP_204_NO_CONTENT
    return response

