
"""One-time CLI bootstrap for the first IUB Lost & Found administrator."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select, update

from app.database import SessionLocal
from app.models import RefreshSession, Student


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def main():
    print("\n=== FIRST ADMINISTRATOR SETUP ===")
    print("This command can run only when no administrator exists.")

    email = input("\nEnter the existing student's registered email: ")
    email = email.strip().lower()

    if not email:
        print("ERROR: Email is required.")
        return

    with SessionLocal() as db:
        try:
            # Allow bootstrap only if no administrator exists.
            admin_count = db.scalar(
                select(func.count(Student.id)).where(
                    Student.role == "admin"
                )
            ) or 0

            if admin_count > 0:
                print(
                    "STOPPED: An administrator already exists. "
                    "Bootstrap cannot be used again."
                )
                return

            # Find an existing registered student.
            student = db.scalar(
                select(Student).where(
                    func.lower(Student.email) == email
                )
            )

            if student is None:
                print("ERROR: No registered student uses this email.")
                return

            if not student.password_hash:
                print("ERROR: This account does not have a password.")
                return

            if student.is_banned:
                print("ERROR: A banned account cannot become administrator.")
                return

            if student.role != "user":
                print("ERROR: This account is not an eligible user account.")
                return

            print("\nACCOUNT SELECTED")
            print("Student ID:", student.student_id)
            print("Full Name:", student.full_name)
            print("Email:", student.email)
            print("Current Role:", student.role)

            print(
                "\nWARNING: Verify that this is the intended "
                "administrator account."
            )

            confirmation = input(
                f"To confirm, type PROMOTE {student.student_id}: "
            ).strip()

            if confirmation != f"PROMOTE {student.student_id}":
                print("CANCELLED: No account was changed.")
                return

            # Promote the selected account.
            now = utcnow()

            student.role = "admin"

            # Invalidate every existing refresh session.
            db.execute(
                update(RefreshSession)
                .where(
                    RefreshSession.student_pk == student.id,
                    RefreshSession.revoked_at.is_(None),
                )
                .values(revoked_at=now)
            )

            db.commit()

            print("\nSUCCESS: First administrator created.")
            print("Student ID:", student.student_id)
            print("Role: admin")
            print("All existing refresh sessions were revoked.")
            print("The administrator must sign in again.")

        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    main()
