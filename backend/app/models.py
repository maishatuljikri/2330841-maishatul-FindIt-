
"""SQLAlchemy database models for IUB Lost & Found."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    false,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Student(Base):
    """Student account and profile information."""

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    student_id: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )

    full_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    # Authentication fields.
    # Nullable values preserve existing demo student records.
    email: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True, nullable=True
    )

    password_hash: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    role: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="user",
        server_default="user",
    )

    is_banned: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
    )

    banned_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    banned_reason: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    password_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    # Existing profile fields.
    phone_number: Mapped[str | None] = mapped_column(
        String(25), nullable=True
    )

    whatsapp_number: Mapped[str | None] = mapped_column(
        String(25), nullable=True
    )

    extra_contact_info: Mapped[str | None] = mapped_column(
        String(240), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Existing relationships.
    items: Mapped[list["Item"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    sessions: Mapped[list["AuthSession"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
    )

    refresh_sessions: Mapped[list["RefreshSession"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_students_role", "role"),
        Index("ix_students_is_banned", "is_banned"),
    )


class AuthSession(Base):
    """Legacy demo sessions retained during authentication migration."""

    __tablename__ = "auth_sessions"

    token_hash: Mapped[str] = mapped_column(
        String(64), primary_key=True
    )

    student_pk: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    student: Mapped[Student] = relationship(
        back_populates="sessions"
    )


class RefreshSession(Base):
    """Hashed refresh tokens and revocable login sessions."""

    __tablename__ = "refresh_sessions"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    token_hash: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )

    student_pk: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Tokens in the same login session share a family ID.
    family_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    replaced_by_token_hash: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(45), nullable=True
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    student: Mapped[Student] = relationship(
        back_populates="refresh_sessions"
    )


class LoginAttempt(Base):
    """Successful and failed authentication attempts."""

    __tablename__ = "login_attempts"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    identifier: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(45), nullable=True, index=True
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    successful: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
    )

    failure_reason: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    attempted_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True
    )


class Item(Base):
    """Lost and found item reports."""

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    title: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )

    description: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(32), nullable=False, index=True
    )

    report_type: Mapped[str] = mapped_column(
        String(12), nullable=False, index=True
    )

    location: Mapped[str] = mapped_column(
        String(120), nullable=False, index=True
    )

    incident_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )

    contact_info: Mapped[str] = mapped_column(
        String(180), nullable=False
    )

    image_data: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(12), default="open", nullable=False, index=True
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True
    )

    owner: Mapped[Student] = relationship(
        back_populates="items"
    )

    __table_args__ = (
        Index("ix_items_board_order", "status", "created_at"),
    )
