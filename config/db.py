"""
author: Tinashe Kucherera
date: 2024-06-20
description: Using SQLite for lightweight, as we go might migrate to a more robust DB.
Database configuration and initialization.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from datetime import datetime, timezone

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # go up one from config/
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'mtl.db')}"
print(DATABASE_URL)

# SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=True  # optional: log SQL queries
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# ======================================================
# ORM Models (matches your current sqlite tables)
# ======================================================
class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    fname = Column(String, nullable=False)
    lname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    driver = relationship("Driver", back_populates="profile", uselist=False)

class Driver(Base):
    __tablename__ = "drivers"
    id = Column(Integer, primary_key=True, index=True)
    license_number = Column(String, nullable=False)
    pay_rate = Column(Float, nullable=False)
    status = Column(String, default="Active")
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    profile = relationship("Profile", back_populates="driver")
    trips = relationship("Trip", back_populates="driver")

class Truck(Base):
    __tablename__ = "trucks"
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    towing_capacity = Column(Float, nullable=False)
    location = Column(String, nullable=True)
    status = Column(String, default="Available")
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    trips = relationship("Trip", back_populates="truck")

class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    broker = Column(String, nullable=False)
    rate_con_number = Column(String, nullable=False)
    rate = Column(Float, nullable=False)
    pickup_location = Column(String, nullable=False)
    dropoff_location = Column(String, nullable=False)
    pickup_date = Column(DateTime, nullable=False)
    delivery_date = Column(DateTime, nullable=False)
    status = Column(String, default="Scheduled")
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    truck_id = Column(Integer, ForeignKey("trucks.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    truck = relationship("Truck", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")

# ======================================================
# Dependency for FastAPI endpoints
# ======================================================
def get_db_session() -> Session:
    """Provide a database session to FastAPI endpoints."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ======================================================
# Create tables if they don't exist
# ======================================================
Base.metadata.create_all(bind=engine)
