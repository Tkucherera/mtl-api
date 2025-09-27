from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
import enum

Base = declarative_base()

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    fname = Column(String)
    lname = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    password = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)

    driver = relationship("Driver", back_populates="profile", uselist=False)


class Driver(Base):
    __tablename__ = "drivers"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    license_number = Column(String)
    pay_rate = Column(Float)
    status = Column(String)

    profile = relationship("Profile", back_populates="driver")
    trips = relationship("Trip", back_populates="driver")


class Truck(Base):
    __tablename__ = "trucks"
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, unique=True)
    model = Column(String)
    year = Column(Integer)
    status = Column(String)
    towing_capacity = Column(Float)
    location = Column(String)

    trips = relationship("Trip", back_populates="truck")




class TripStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    IN_TRANSIT = "IN_TRANSIT"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    broker = Column(String)
    rate_con_number = Column(String)
    rate = Column(Float)
    pickup_location = Column(String)
    dropoff_location = Column(String)
    pickup_date = Column(DateTime)
    delivery_date = Column(DateTime)
    status = Column(Enum(TripStatus), nullable=False, default=TripStatus.SCHEDULED)
    truck_id = Column(Integer, ForeignKey("trucks.id"))
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))

    truck = relationship("Truck", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")
