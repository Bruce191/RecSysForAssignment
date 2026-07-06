from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
import os

db_path = Path(__file__).parent / "local.db"

DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{db_path.absolute()}")

# connect_args is only needed for SQLite, not Postgres
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# --- Debug info: shows which database this app is actually connected to ---
if DATABASE_URL.startswith("sqlite"):
    print(f"[DB] Using local SQLite database at: {db_path.absolute()}")
else:
    # avoid printing the full URL in case it contains a password
    safe_url = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
    print(f"[DB] Using PostgreSQL database at: {safe_url}")

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()