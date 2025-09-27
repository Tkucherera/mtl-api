from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models import TripStatus
# -----------------------
# Auth Schemas
# -----------------------
class Token(BaseModel):
    access_token: str
    token_type: str

# -----------------------
# Profile Schemas
# -----------------------
class ProfileBase(BaseModel):
    fname: str
    lname: str
    email: EmailStr
    phone: Optional[str] = None

class ProfileCreate(ProfileBase):
    password: str   # plain password input

class ProfileOut(ProfileBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

# -----------------------
# Driver Schemas
# -----------------------
class DriverBase(BaseModel):
    license_number: str
    pay_rate: float
    status: Optional[str] = "Active"

class DriverCreate(DriverBase):
    profile: ProfileCreate   # nested create with profile

class DriverOut(DriverBase):
    id: int
    profile: ProfileOut
    class Config:
        orm_mode = True
        from_attributes = True

# -----------------------
# Truck Schemas
# -----------------------
class TruckBase(BaseModel):
    plate_number: str
    model: str
    year: int
    towing_capacity: float
    status: Optional[str] = "Available"
    location: Optional[str] = None

class TruckCreate(TruckBase):
    pass

class TruckUpdate(BaseModel):
    plate_number: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    towing_capacity: Optional[float] = None
    status: Optional[str] = None
    location: Optional[str] = None

class TruckOut(TruckBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

# -----------------------
# Trip Schemas
# -----------------------
class TripBase(BaseModel):
    broker: str
    rate_con_number: str
    rate: float
    pickup_location: str
    dropoff_location: str
    pickup_date: datetime
    delivery_date: datetime
    status: Optional[str] = "Scheduled"

class TripCreate(TripBase):
    truck_id: Optional[int] = None
    driver_id: Optional[int] = None
    status: TripStatus = TripStatus.SCHEDULED

class TripUpdate(BaseModel):
    broker: Optional[str] = None
    rate_con_number: Optional[str] = None
    rate: Optional[float] = None
    pickup_location: Optional[str] = None
    dropoff_location: Optional[str] = None
    pickup_date: Optional[datetime] = None
    delivery_date: Optional[datetime] = None
    truck_id: Optional[int] = None
    driver_id: Optional[int] = None
    status: Optional[str] = None

class TripOut(TripBase):
    id: int
    status: TripStatus
    created_at: datetime
    updated_at: datetime
    truck: Optional[TruckOut] = None
    driver: Optional[DriverOut] = None

    class Config:
        orm_mode = True
        from_attributes = True
