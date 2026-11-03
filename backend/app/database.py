"""Database configuration for the IUB Lost & Found demo."""



import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


def get_database_url() -> str:
    """Get and normalize the database connection URL."""

    database_url = os.getenv("DATABASE_URL")

    # Never silently use temporary SQLite storage on Vercel.
    if not database_url:
        if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
            raise RuntimeError(
                "DATABASE_URL is missing from Vercel environment variables."
            )

        # Local development fallback only.
        database_url = "sqlite:///./data/lost_found.db"

    # Normalize older PostgreSQL URL formats.
    if database_url.startswith("postgres://"):
        database_url = "postgresql://" + database_url[len("postgres://"):]

    # Explicitly use the installed Psycopg 3 driver.
    if database_url.startswith("postgresql://"):
        database_url = (
            "postgresql+psycopg://"
            + database_url[len("postgresql://"):]
        )

    return database_url


DATABASE_URL = get_database_url()

# Create local SQLite directory only during local development.
if DATABASE_URL.startswith("sqlite:///") and DATABASE_URL != "sqlite:///:memory:":
    db_file = DATABASE_URL.replace("sqlite:///", "", 1)
    Path(db_file).parent.mkdir(parents=True, exist_ok=True)

connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()