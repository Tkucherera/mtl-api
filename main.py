from fastapi import FastAPI, Depends, HTTPException, status, Response, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from typing import Union, List, Annotated
from datetime import timedelta, datetime
from sqlalchemy.orm import Session

from config.db import get_db_session, engine
import models , schemas, security

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="MTL API", description="API for Managing Truck Loads", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:5173'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def read_root():
    return {"message": "Welcome to the MTL API. Use /docs for API documentation."}


"""
 User Endpoints 
"""
@app.post("/api/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_session)):
    user = db.query(models.Profile).filter(models.Profile.email == form_data.username).first()

    if not user or not security.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/drivers/", response_model=schemas.DriverOut, status_code=201)
def create_driver(data: schemas.DriverCreate, db: Session = Depends(get_db_session)):
    # Hash password inside Profile
    hashed_pw = security.get_password_hash(data.profile.password)
    profile = models.Profile(
        fname=data.profile.fname,
        lname=data.profile.lname,
        email=data.profile.email,
        phone=data.profile.phone,
        password=hashed_pw
    )
    driver = models.Driver(
        license_number=data.license_number,
        pay_rate=data.pay_rate,
        status=data.status,
        profile=profile
    )
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@app.get("/api/drivers/{driver_id}", response_model=schemas.DriverOut)
def get_driver(driver_id: int, db: Session = Depends(get_db_session)):
    driver = db.query(models.Driver).filter(models.Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver

@app.post("/api/trucks/", response_model=schemas.TruckOut, status_code=201)
def create_truck(data: schemas.TruckCreate, db: Session = Depends(get_db_session)):
    truck = models.Truck(**data.dict())
    db.add(truck)
    db.commit()
    db.refresh(truck)
    return truck


@app.get("/api/trucks/", response_model=List[schemas.TruckOut])
def get_trucks(status: Union[str, None] = None, db: Session = Depends(get_db_session)):
    query = db.query(models.Truck)
    if status:
        query = query.filter(models.Truck.status == status)
    return query.all()


@app.post("/api/trips/", response_model=schemas.TripOut, status_code=201)
def create_trip(data: schemas.TripCreate, db: Session = Depends(get_db_session)):
    trip = models.Trip(**data.dict())
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@app.get("/api/trips/", response_model=List[schemas.TripOut])
def get_trips(
    broker: Union[str, None] = None,
    driver_id: Union[int, None] = None,
    db: Session = Depends(get_db_session)
):
    query = db.query(models.Trip)
    if broker:
        query = query.filter(models.Trip.broker == broker)
    if driver_id:
        query = query.filter(models.Trip.driver_id == driver_id)
    return query.all()


@app.get("/api/trips/{trip_id}", response_model=schemas.TripOut)
def get_trip(trip_id: int, db: Session = Depends(get_db_session)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@app.put("/api/trips/{trip_id}", response_model=schemas.TripOut)
def update_trip(trip_id: int, data: schemas.TripUpdate, db: Session = Depends(get_db_session)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(trip, field, value)
    db.commit()
    db.refresh(trip)
    return trip


"""
Authenticated Endpoints 
"""
@app.get('/api/driver/me', response_model=schemas.DriverOut)
def get_current_driver(
    current_user: Annotated[schemas.DriverOut, Depends(security.get_current_driver)]):
    return current_user

@app.get('/api/driver/mytrips/', response_model=List[schemas.TripOut])
def get_driver_trips(
    current_user: Annotated[schemas.DriverOut, Depends(security.get_current_driver)], db: Session = Depends(get_db_session)):

    query = db.query(models.Trip).filter(models.Trip.driver_id == current_user.id)
    return query.all()

@app.get('/api/driver/current_trip/')
def get_current_trip(
    current_driver: Annotated[schemas.DriverOut, Depends(security.get_current_driver)], db: Session = Depends(get_db_session)):

    current_trip = db.query(models.Trip).filter(
        models.Trip.driver_id == current_driver.id,
        models.Trip.status.in_(["ONGOING", "IN_TRANSIT"])
    ).first()
        
    return current_trip if current_trip else {'current_trip': None}
