from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base,Session
from fastapi import Depends
from typing import Annotated
# SQLite URL (file-based)
SQLALCHEMY_DATABASE_URL = "sqlite:///./bank.db"

# Engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def init_db():
    """Initialize database (create tables)."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Yield a SQLAlchemy session for FastAPI dependencies."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        