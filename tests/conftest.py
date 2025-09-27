import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import pytest
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Profile, Driver, Truck, Trip
from fastapi.testclient import TestClient
from main import app
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Load JSON seed data
    with open("test-data/json_db/db.json") as f:
        data = json.load(f)
    drivers_data = data['drivers']
    trucks_data = data['trucks']
    trips_data = data['trips']

    

    db = TestingSessionLocal()

    # Seed drivers + profiles
    for d in drivers_data:
        p = Profile(**d["profile"])
        driver = Driver(
            id=d["id"],
            license_number=d["license_number"],
            pay_rate=d["pay_rate"],
            status=d["status"],
            profile=p
        )
        db.add(driver)

    # Seed trucks
    for t in trucks_data:
        db.add(Truck(**t))

    # Seed trips
    for t in trips_data:
        trip = Trip(
            id=t["id"],
            broker=t["broker"],
            rate_con_number=t["rate_con_number"],
            rate=t["rate"],
            pickup_location=t["pickup_location"],
            dropoff_location=t["dropoff_location"],
            pickup_date=datetime.fromisoformat(t["pickup_date"]),
            delivery_date=datetime.fromisoformat(t["delivery_date"]),
            status=t["status"],
            truck_id=t["truck"]["id"],
            driver_id=t["driver"]["id"]
        )
        db.add(trip)

    db.commit()
    db.close()

    yield  # Run tests

    # Reset DB for reruns
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)
