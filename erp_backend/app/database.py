import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session

# SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./erp.db"

# Create SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    pool_pre_ping=True
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def init_db():
    """Initialize the database by creating all tables"""
    # Import models to ensure they are registered with SQLAlchemy
    from . import models
    
    # Drop all tables if in development mode
    if os.getenv("ENVIRONMENT", "development") == "development":
        Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency function to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
