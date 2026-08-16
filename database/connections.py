from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# SQLite URL (file-based)
SQLALCHEMY_DATABASE_URL = "sqlite:///./bank.db"

# Engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def init_db():
    """Initialize database (create tables)."""
    Base.metadata.create_all(bind=engine)
