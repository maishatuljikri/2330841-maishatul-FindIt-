"""FastAPI application for the IUB Lost & Found project."""
from __future__ import annotations

import base64
from contextlib import asynccontextmanager
from datetime import date, timedelta
import os

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy import func, inspect, or_, select, text
from sqlalchemy.orm import Session, joinedload

from .database import Base, SessionLocal, engine, get_db
from .dependencies import get_jwt_current_user, get_optional_jwt_user
from .models import Item, Student
from .routers.auth import router as auth_router
from .routers.admin import router as admin_router
from .schemas import (
    ContactResponse,
    ItemCreate,
    ItemPublic,
    ItemStatusUpdate,
    ItemUpdate,
    StatsResponse,
)


def _migrate_legacy_demo_columns() -> None:
    """Add only legacy demo columns missing from an older local database.

    The main schema is managed by Alembic. This small compatibility helper
    remains for the original demo's profile/photo columns only.
    """
    with engine.begin() as connection:
        inspector = inspect(connection)
        tables = set(inspector.get_table_names())

        if "students" in tables:
            student_columns = {
                column["name"]
                for column in inspector.get_columns("students")
            }
            additions = {
                "phone_number": "VARCHAR(25)",
                "whatsapp_number": "VARCHAR(25)",
                "extra_contact_info": "VARCHAR(240)",
            }
            for column_name, column_type in additions.items():
                if column_name not in student_columns:
                    connection.execute(
                        text(
                            f"ALTER TABLE students "
                            f"ADD COLUMN {column_name} {column_type}"
                        )
                    )

        if "items" in tables:
            item_columns = {
                column["name"]
                for column in inspector.get_columns("items")
            }
            if "image_data" not in item_columns:
                connection.execute(
                    text("ALTER TABLE items ADD COLUMN image_data TEXT")
                )


def _utcnow_naive():
    """Return UTC time as a naive datetime for existing DateTime columns."""
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).replace(tzinfo=None)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize missing tables and seed the demo board.

    Existing databases must be upgraded with Alembic before deployment.
    create_all() creates missing tables but does not alter existing tables.
    """
    Base.metadata.create_all(bind=engine)
    _migrate_legacy_demo_columns()

    with SessionLocal() as db:
        _seed_demo_data(db)

    yield


app = FastAPI(
    title="IUB Lost & Found API",
    description=(
        "A CSE309 campus lost-and-found application with JWT authentication."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# Register the new authentication endpoints exactly once.
app.include_router(auth_router)
app.include_router(admin_router)

configured_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in configured_origins.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Keep the names used by the existing CRUD endpoints, but resolve users
# through JWT instead of the old seven-day demo bearer token.
get_current_user = get_jwt_current_user
get_optional_user = get_optional_jwt_user


def _serialize_item(
    item: Item,
    user: Student | None = None,
    include_contact: bool = False,
) -> dict:
    """Convert an Item model to the public API response shape."""
    return {
        "id": item.id,
        "title": item.title,
        "description": item.description,
        "category": item.category,
        "report_type": item.report_type,
        "location": item.location,
        "incident_date": item.incident_date,
        "status": item.status,
        "reporter_name": item.owner.full_name,
        "created_at": item.created_at,
        "is_owner": bool(user and user.id == item.owner_id),
        "contact_available": True,
        # Contact details are only returned to an authenticated owner here.
        "contact_info": item.contact_info if include_contact and user else None,
        "image_url": f"/api/items/{item.id}/image" if item.image_data else None,
    }


def _seed_demo_data(db: Session) -> None:
    """Insert sample board data only when the items table is empty."""
    if (db.scalar(select(func.count(Item.id))) or 0) != 0:
        return

    demo_students = [
        Student(student_id="DEMO-1001", full_name="Ayesha Rahman"),
        Student(student_id="DEMO-1002", full_name="Tanvir Hasan"),
        Student(student_id="DEMO-1003", full_name="Nabila Chowdhury"),
        Student(student_id="DEMO-1004", full_name="Samiul Islam"),
        Student(student_id="DEMO-1005", full_name="Maliha Ahmed"),
    ]
    db.add_all(demo_students)
    db.flush()

    today = date.today()
    samples = [
        Item(
            title="Black wireless earbuds case",
            description=(
                "A small black earbuds case was left behind after the afternoon "
                "class. Please share the brand or a detail to confirm ownership."
            ),
            category="Electronics",
            report_type="found",
            location="Library — 2nd floor study area",
            incident_date=today - timedelta(days=1),
            contact_info="Ask for the Lost & Found desk at the library counter.",
            owner_id=demo_students[0].id,
        ),
        Item(
            title="Blue university notebook",
            description=(
                "I misplaced a blue spiral notebook with lecture notes inside. "
                "It has a small white sticker on the front cover."
            ),
            category="Books",
            report_type="lost",
            location="School of Business corridor",
            incident_date=today - timedelta(days=2),
            contact_info="Send a message through the campus student community.",
            owner_id=demo_students[1].id,
        ),
        Item(
            title="Silver keyring with two keys",
            description=(
                "Found a silver keyring with two keys near the main cafeteria "
                "seating area. Kept safe while waiting for its owner."
            ),
            category="Keys",
            report_type="found",
            location="Main cafeteria entrance",
            incident_date=today - timedelta(days=1),
            contact_info="Please describe the keyring at the campus help desk.",
            owner_id=demo_students[2].id,
        ),
        Item(
            title="Student card in a clear sleeve",
            description=(
                "A student card was misplaced around the academic building. "
                "The card is inside a clear plastic sleeve."
            ),
            category="Cards & IDs",
            report_type="lost",
            location="Academic Building — ground floor",
            incident_date=today - timedelta(days=3),
            contact_info=(
                "Please contact me through the campus help desk. "
                "Do not post card details publicly."
            ),
            owner_id=demo_students[3].id,
        ),
        Item(
            title="Olive green water bottle",
            description=(
                "Found an olive green reusable bottle after a morning study "
                "session. It has a small round sticker near the bottom."
            ),
            category="Accessories",
            report_type="found",
            location="Student lounge",
            incident_date=today - timedelta(days=4),
            contact_info="Ask for the item at the student lounge reception.",
            owner_id=demo_students[4].id,
        ),
        Item(
            title="Grey laptop sleeve",
            description=(
                "A grey 14-inch laptop sleeve may have been left in a classroom. "
                "There is no laptop inside it."
            ),
            category="Bags",
            report_type="lost",
            location="Room 402, academic building",
            incident_date=today - timedelta(days=5),
            contact_info=(
                "Message via the student community and mention the sleeve size."
            ),
            owner_id=demo_students[0].id,
        ),
    ]
    db.add_all(samples)
    db.commit()


@app.get("/api/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "IUB Lost & Found API"}


@app.get("/api/stats", response_model=StatsResponse, tags=["board"])
def stats(db: Session = Depends(get_db)) -> dict[str, int]:
    total = db.scalar(select(func.count(Item.id))) or 0
    open_count = db.scalar(
        select(func.count(Item.id)).where(Item.status == "open")
    ) or 0
    resolved = db.scalar(
        select(func.count(Item.id)).where(Item.status == "resolved")
    ) or 0
    lost = db.scalar(
        select(func.count(Item.id)).where(Item.report_type == "lost")
    ) or 0
    found = db.scalar(
        select(func.count(Item.id)).where(Item.report_type == "found")
    ) or 0
    return {
        "total_reports": total,
        "open_reports": open_count,
        "resolved_reports": resolved,
        "lost_reports": lost,
        "found_reports": found,
    }


@app.get("/api/items", response_model=list[ItemPublic], tags=["board"])
def list_items(
    q: str | None = Query(default=None, max_length=100),
    category: str | None = Query(default=None, max_length=32),
    report_type: str | None = Query(default=None, pattern="^(lost|found)$"),
    item_status: str | None = Query(
        default="open", alias="status", pattern="^(open|resolved|all)$"
    ),
    db: Session = Depends(get_db),
    current_user: Student | None = Depends(get_optional_user),
) -> list[dict]:
    query = select(Item).options(joinedload(Item.owner))

    if item_status and item_status != "all":
        query = query.where(Item.status == item_status)
    if category and category != "All items":
        query = query.where(Item.category == category)
    if report_type:
        query = query.where(Item.report_type == report_type)
    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.where(
            or_(
                Item.title.ilike(term),
                Item.description.ilike(term),
                Item.location.ilike(term),
                Item.category.ilike(term),
            )
        )

    items = db.scalars(
        query.order_by(Item.created_at.desc(), Item.id.desc()).limit(100)
    ).unique().all()

    return [_serialize_item(item, current_user) for item in items]


@app.get("/api/items/{item_id}", response_model=ItemPublic, tags=["board"])
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Student | None = Depends(get_optional_user),
) -> dict:
    """Read one report; only its owner receives contact instructions."""
    item = db.scalar(
        select(Item)
        .options(joinedload(Item.owner))
        .where(Item.id == item_id)
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This report could not be found.",
        )

    is_owner = bool(current_user and current_user.id == item.owner_id)
    return _serialize_item(item, current_user, include_contact=is_owner)


@app.post(
    "/api/items",
    response_model=ItemPublic,
    status_code=status.HTTP_201_CREATED,
    tags=["board"],
)
def create_item(
    payload: ItemCreate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
) -> dict:
    item = Item(
        title=payload.title,
        description=payload.description,
        category=payload.category,
        report_type=payload.report_type,
        location=payload.location,
        incident_date=payload.incident_date,
        contact_info=payload.contact_info,
        image_data=payload.image_data,
        owner_id=current_user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    item = db.scalar(
        select(Item)
        .options(joinedload(Item.owner))
        .where(Item.id == item.id)
    )
    return _serialize_item(item, current_user)


@app.put("/api/items/{item_id}", response_model=ItemPublic, tags=["board"])
def update_item(
    item_id: int,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
) -> dict:
    """Update a report. Only its owner may modify it."""
    item = db.scalar(
        select(Item)
        .options(joinedload(Item.owner))
        .where(Item.id == item_id)
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This report could not be found.",
        )
    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reports.",
        )

    changes = payload.model_dump(exclude_unset=True)
    for field in (
        "title",
        "description",
        "category",
        "report_type",
        "location",
        "incident_date",
        "contact_info",
    ):
        if field in changes:
            setattr(item, field, changes[field])

    # Omitted image_data preserves the existing image; explicit null removes it.
    if "image_data" in changes:
        item.image_data = changes["image_data"]

    db.commit()
    db.refresh(item)

    item = db.scalar(
        select(Item)
        .options(joinedload(Item.owner))
        .where(Item.id == item_id)
    )
    return _serialize_item(item, current_user, include_contact=True)


@app.get("/api/items/{item_id}/image", tags=["board"])
def get_item_image(item_id: int, db: Session = Depends(get_db)) -> Response:
    """Serve an item's stored Base64 image."""
    item = db.get(Item, item_id)
    if item is None or not item.image_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This report has no photo.",
        )

    try:
        header, encoded = item.image_data.split(",", 1)
        media_type = header.removeprefix("data:").removesuffix(";base64")
        content = base64.b64decode(encoded, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The stored report photo is invalid.",
        ) from exc

    return Response(
        content=content,
        media_type=media_type,
        headers={"Cache-Control": "public, max-age=3600"},
    )


@app.get(
    "/api/items/{item_id}/contact",
    response_model=ContactResponse,
    tags=["board"],
)
def get_contact(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
) -> dict[str, str | None]:
    item = db.scalar(
        select(Item)
        .options(joinedload(Item.owner))
        .where(Item.id == item_id)
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This report could not be found.",
        )

    return {
        "reporter_name": item.owner.full_name,
        "phone_number": item.owner.phone_number,
        "whatsapp_number": item.owner.whatsapp_number or item.owner.phone_number,
        "extra_contact_info": item.owner.extra_contact_info,
        "contact_info": item.contact_info,
    }


@app.patch(
    "/api/items/{item_id}/status",
    response_model=ItemPublic,
    tags=["board"],
)
def update_status(
    item_id: int,
    payload: ItemStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
) -> dict:
    item = db.scalar(
        select(Item)
        .options(joinedload(Item.owner))
        .where(Item.id == item_id)
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This report could not be found.",
        )
    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reports.",
        )

    item.status = payload.status
    db.commit()
    db.refresh(item)

    item = db.scalar(
        select(Item)
        .options(joinedload(Item.owner))
        .where(Item.id == item_id)
    )
    return _serialize_item(item, current_user)


@app.delete(
    "/api/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["board"],
)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
) -> None:
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This report could not be found.",
        )
    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reports.",
        )

    db.delete(item)
    db.commit()
    return None
