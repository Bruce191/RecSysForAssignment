from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

# db_path = Path(__file__).parent / "local.db"

# DATABASE_URL = f"sqlite:///{db_path.absolute()}"

# engine = create_engine(
#     DATABASE_URL,
#     connect_args={"check_same_thread": False}
# )

# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine
# )

# Base = declarative_base()


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

db_path = Path(__file__).parent / "local.db"

DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{db_path.absolute()}")

# connect_args is only needed for SQLite, not Postgres
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

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