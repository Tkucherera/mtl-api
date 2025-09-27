"""
author: Tinashe Kucherera
date: 2024-06-20
description: Running tests for server side application.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# tests/test_models.py
import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Profile, Driver, Truck, Trip

# SQLite in-memory DB for pure unit tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Session = sessionmaker(bind=engine)


@pytest.fixture(scope="function", autouse=True)
def db_session():
    """Create fresh database tables for each test"""
    Base.metadata.create_all(engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_create_profile_and_driver(db_session):
    profile = Profile(
        fname="Alice",
        lname="Johnson",
        email="alice@example.com",
        phone="555-0001",
        password=None,
        profile_picture=None
    )
    driver = Driver(
        license_number="DL-11111",
        pay_rate=0.60,
        status="ACTIVE",
        profile=profile
    )
    db_session.add(driver)
    db_session.commit()

    stored_driver = db_session.query(Driver).first()
    assert stored_driver.profile.fname == "Alice"
    assert stored_driver.profile.email == "alice@example.com"
    assert stored_driver.license_number == "DL-11111"


def test_create_truck(db_session):
    truck = Truck(
        plate_number="NC-4455",
        model="Volvo VNL",
        year=2022,
        status="AVAILABLE"
    )
    db_session.add(truck)
    db_session.commit()

    stored_truck = db_session.query(Truck).first()
    assert stored_truck.model == "Volvo VNL"
    assert stored_truck.status == "AVAILABLE"


def test_trip_relationships(db_session):
    # create driver + truck
    profile = Profile(fname="Bob", lname="Smith", email="bob@example.com", phone="555-0002")
    driver = Driver(license_number="DL-22222", pay_rate=0.70, status="ACTIVE", profile=profile)
    truck = Truck(plate_number="TX-9999", model="Kenworth T680", year=2023, status="IN_SERVICE")
    db_session.add_all([driver, truck])
    db_session.commit()

    # create trip
    trip = Trip(
        broker="Test Logistics",
        rate_con_number="RC-555",
        rate=2000.0,
        pickup_location="Houston, TX",
        dropoff_location="Miami, FL",
        pickup_date=datetime.now(timezone.utc),
        delivery_date=datetime.now(timezone.utc) + timedelta(days=2),
        status="SCHEDULED",
        truck_id=truck.id,
        driver_id=driver.id,
    )
    db_session.add(trip)
    db_session.commit()

    stored_trip = db_session.query(Trip).first()
    assert stored_trip.driver.profile.lname == "Smith"
    assert stored_trip.truck.model == "Kenworth T680"
    assert stored_trip.broker == "Test Logistics"


def test_trip_timestamps_autoset(db_session):
    truck = Truck(plate_number="GA-7777", model="Freightliner Cascadia", year=2021, status="AVAILABLE")
    db_session.add(truck)
    db_session.commit()

    trip = Trip(
        broker="Quick Haul",
        rate_con_number="RC-777",
        rate=1800.0,
        pickup_location="Atlanta, GA",
        dropoff_location="Charlotte, NC",
        pickup_date=datetime.now(tz=timezone.utc),
        delivery_date=datetime.now(tz=timezone.utc) + timedelta(days=1),
        status="SCHEDULED",
        truck_id=truck.id
    )
    db_session.add(trip)
    db_session.commit()

    stored_trip = db_session.query(Trip).first()
    assert stored_trip.created_at is not None
    assert stored_trip.updated_at is not None
    assert isinstance(stored_trip.created_at, datetime)






def test_create_profile_and_driver(db_session):
    profile = Profile(
        fname="Alice",
        lname="Johnson",
        email="alice@example.com",
        phone="555-0001",
        password=None,
        profile_picture=None
    )
    driver = Driver(
        license_number="DL-11111",
        pay_rate=0.60,
        status="ACTIVE",
        profile=profile
    )
    db_session.add(driver)
    db_session.commit()

    stored_driver = db_session.query(Driver).first()
    assert stored_driver.profile.fname == "Alice"
    assert stored_driver.profile.email == "alice@example.com"
    assert stored_driver.license_number == "DL-11111"


def test_create_truck(db_session):
    truck = Truck(
        plate_number="NC-4455",
        model="Volvo VNL",
        year=2022,
        status="AVAILABLE"
    )
    db_session.add(truck)
    db_session.commit()

    stored_truck = db_session.query(Truck).first()
    assert stored_truck.model == "Volvo VNL"
    assert stored_truck.status == "AVAILABLE"


def test_trip_relationships(db_session):
    # create driver + truck
    profile = Profile(fname="Bob", lname="Smith", email="bob@example.com", phone="555-0002")
    driver = Driver(license_number="DL-22222", pay_rate=0.70, status="ACTIVE", profile=profile)
    truck = Truck(plate_number="TX-9999", model="Kenworth T680", year=2023, status="IN_SERVICE")
    db_session.add_all([driver, truck])
    db_session.commit()

    # create trip
    trip = Trip(
        broker="Test Logistics",
        rate_con_number="RC-555",
        rate=2000.0,
        pickup_location="Houston, TX",
        dropoff_location="Miami, FL",
        pickup_date=datetime.now(timezone.utc),
        delivery_date=datetime.now(timezone.utc) + timedelta(days=2),
        status="SCHEDULED",
        truck_id=truck.id,
        driver_id=driver.id,
    )
    db_session.add(trip)
    db_session.commit()

    stored_trip = db_session.query(Trip).first()
    assert stored_trip.driver.profile.lname == "Smith"
    assert stored_trip.truck.model == "Kenworth T680"
    assert stored_trip.broker == "Test Logistics"


def test_trip_timestamps_autoset(db_session):
    truck = Truck(plate_number="GA-7777", model="Freightliner Cascadia", year=2021, status="AVAILABLE")
    db_session.add(truck)
    db_session.commit()

    trip = Trip(
        broker="Quick Haul",
        rate_con_number="RC-777",
        rate=1800.0,
        pickup_location="Atlanta, GA",
        dropoff_location="Charlotte, NC",
        pickup_date=datetime.now(timezone.utc),
        delivery_date=datetime.now(timezone.utc) + timedelta(days=1),
        status="SCHEDULED",
        truck_id=truck.id
    )
    db_session.add(trip)
    db_session.commit()

    stored_trip = db_session.query(Trip).first()
    assert stored_trip.created_at is not None
    assert stored_trip.updated_at is not None
    assert isinstance(stored_trip.created_at, datetime)
