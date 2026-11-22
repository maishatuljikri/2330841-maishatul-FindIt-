
"""Admin-only APIs for IUB Lost & Found."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_roles
from ..models import Item, RefreshSession, Student
from ..schemas import (
    AdminBanRequest,
    AdminOverviewResponse,
    AdminStudentPublic,
)


router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
)


def _utcnow() -> datetime:
    """Return UTC time as a naive datetime for SQLAlchemy columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


# =====================================================
# ADMIN DASHBOARD OVERVIEW
# =====================================================

@router.get(
    "/overview",
    response_model=AdminOverviewResponse,
)
def admin_overview(
    db: Session = Depends(get_db),
    admin: Student = Depends(require_roles("admin")),
) -> dict[str, int]:
    """Return student and report statistics for the admin dashboard."""

    total_students = db.scalar(
        select(func.count(Student.id))
    ) or 0

    active_students = db.scalar(
        select(func.count(Student.id)).where(
            Student.is_banned.is_(False)
        )
    ) or 0

    banned_students = db.scalar(
        select(func.count(Student.id)).where(
            Student.is_banned.is_(True)
        )
    ) or 0

    admin_count = db.scalar(
        select(func.count(Student.id)).where(
            Student.role == "admin"
        )
    ) or 0

    total_reports = db.scalar(
        select(func.count(Item.id))
    ) or 0

    open_reports = db.scalar(
        select(func.count(Item.id)).where(
            Item.status == "open"
        )
    ) or 0

    resolved_reports = db.scalar(
        select(func.count(Item.id)).where(
            Item.status == "resolved"
        )
    ) or 0

    return {
        "total_students": total_students,
        "active_students": active_students,
        "banned_students": banned_students,
        "admin_count": admin_count,
        "total_reports": total_reports,
        "open_reports": open_reports,
        "resolved_reports": resolved_reports,
    }


# =====================================================
# STUDENT LIST AND SEARCH
# =====================================================

@router.get(
    "/students",
    response_model=list[AdminStudentPublic],
)
def list_students(
    q: str | None = Query(default=None, max_length=100),
    student_status: str = Query(
        default="all",
        alias="status",
        pattern="^(all|active|banned)$",
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    admin: Student = Depends(require_roles("admin")),
) -> list[Student]:
    """Search and list students. Admin access is required."""

    query = select(Student)

    if q and q.strip():
        term = f"%{q.strip()}%"

        query = query.where(
            or_(
                Student.student_id.ilike(term),
                Student.full_name.ilike(term),
                Student.email.ilike(term),
            )
        )

    if student_status == "active":
        query = query.where(
            Student.is_banned.is_(False)
        )

    elif student_status == "banned":
        query = query.where(
            Student.is_banned.is_(True)
        )

    return db.scalars(
        query.order_by(
            Student.created_at.desc(),
            Student.id.desc(),
        )
        .limit(limit)
        .offset(offset)
    ).all()


# =====================================================
# BAN A STUDENT
# =====================================================

@router.patch(
    "/students/{student_pk}/ban",
    response_model=AdminStudentPublic,
)
def ban_student(
    student_pk: int,
    payload: AdminBanRequest,
    db: Session = Depends(get_db),
    admin: Student = Depends(require_roles("admin")),
) -> Student:
    """Ban a student and revoke all their active refresh sessions."""

    target = db.get(Student, student_pk)

    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student account not found.",
        )

    # Prevent an administrator from banning their own account.
    if target.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot ban your own administrator account.",
        )

    # Public student-management actions must not modify administrators.
    if target.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator accounts cannot be banned here.",
        )

    if target.is_banned:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This student is already banned.",
        )

    now = _utcnow()

    target.is_banned = True
    target.banned_at = now
    target.banned_reason = payload.reason

    # Immediately invalidate all refresh sessions belonging to this student.
    db.execute(
        update(RefreshSession)
        .where(
            RefreshSession.student_pk == target.id,
            RefreshSession.revoked_at.is_(None),
        )
        .values(revoked_at=now)
    )

    db.commit()
    db.refresh(target)

    return target


# =====================================================
# UNBAN A STUDENT
# =====================================================

@router.patch(
    "/students/{student_pk}/unban",
    response_model=AdminStudentPublic,
)
def unban_student(
    student_pk: int,
    db: Session = Depends(get_db),
    admin: Student = Depends(require_roles("admin")),
) -> Student:
    """Restore a previously banned student account."""

    target = db.get(Student, student_pk)

    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student account not found.",
        )

    if target.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator accounts cannot be modified here.",
        )

    if not target.is_banned:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This student is not currently banned.",
        )

    target.is_banned = False
    target.banned_at = None
    target.banned_reason = None

    db.commit()
    db.refresh(target)

    # Existing sessions remain revoked.
    # The student must sign in again to create a new session.

    return target
