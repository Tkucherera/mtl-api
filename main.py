import sys
import os


from services.trip import Trip, TripItem
from logger import activity_logger, error_logger, stdout_logger
from services.extract_trip_details import extract_from_pdf, process_pdf_text
import messages as msg
from config.db import get_db_connection
from client import Client



from typing import Union
from fastapi import FastAPI, File, UploadFile, Form
from fastapi import Response, status
from datetime import datetime



app = FastAPI(title="MTL API", description="API for Managing Truck Loads", version="1.0.0")


# see if we can filter


session = None
session = Client()

@app.get("/")
def read_root():
    """
    Root endpoint providing
    Need to return multiple content
    - A welcome message
    - User meta data

    """
    return {"message": "Welcome to the MTL API. Use /docs for API documentation."}

"""
Work on Trip endpoints
"""
@app.get('/api/trips/')
def get_trips(
        broker: Union[str, None] = None,
        rate: Union[float, None] = None,
        rate_con_number: Union[str, None] = None, 
        status: Union[str, None] = None,
        driver_id: Union[int, None] = None,
        truck_id: Union[int, None] = None,
        pick_up_location: Union[str, None] = None,
        drop_off_location: Union[str, None] = None,
        end_date: Union[str, None] = None):
    """
    Get all trips or filter by passing optional query params
    """
    conn = get_db_connection()
    trips = Trip.filter(conn, broker=broker, rate=rate, rate_con_number=rate_con_number, status=status, driver_id=driver_id, truck_id=truck_id)

    return trips.raw()

@app.get("/api/trips/{trip_id}", status_code=200)
def get_trip(trip_id: int, response: Response):
    """
    Get trip details by trip ID.
    """
    conn = get_db_connection()
    trip = Trip.get(conn, trip_id)
    if trip.apicode == 404:
        response.status_code = status.HTTP_404_NOT_FOUND
    return trip.raw()

@app.post("/api/trips/", status_code=201)       
def create_trip(trip: TripItem, response: Response): 
    """
    Create a new trip.
    TODO Support forms as well
    """
    conn = get_db_connection()
    new_trip = Trip(trip.broker, 
                    trip.rate_con_number, 
                    trip.rate, 
                    trip.pickup_location, 
                    trip.dropoff_location, 
                    trip.pickup_date,
                    trip.delivery_date, 
                    trip.truck_id, 
                    trip.status)
    res = new_trip.create(conn, new_trip.__dict__)
    if res.apicode == 400:
        response.status_code = status.HTTP_400_BAD_REQUEST
    return res.raw()

@app.put("/api/trips/{trip_id}/")
def update_trip_status(trip_id: int, 
        broker: Union[str, None] = None,
        rate: Union[float, None] = None,
        rate_con_number: Union[str, None] = None, 
        status: Union[str, None] = None,
        driver_id: Union[int, None] = None,
        truck_id: Union[int, None] = None,
        pick_up_location: Union[str, None] = None,
        drop_off_location: Union[str, None] = None,
        end_date: Union[str, None] = None):
    """
    Update the values of a trip.
    """
    conn = get_db_connection()
    res = Trip.update(conn, trip_id, broker=broker, rate=rate, rate_con_number=rate_con_number, status=status, driver_id=driver_id, truck_id=truck_id)
    conn.close()
    return res.raw()



@app.post("/api/trips/upload")
def upload_trip_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file containing trip details.
    The PDF will be processed to extract trip information.
    """
    if not file.filename.endswith('.pdf'):
        return {"apicode": 400, "message": "Only PDF files are supported."}

    file_location = f"/tmp/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    resp = extract_from_pdf(file_location)
    os.remove(file_location)  # Clean up the temporary file

    if resp.apicode == 201:
        content = resp.raw()
        text = content['created']['raw_text']
        trip_data = process_pdf_text(text)
        return {"apicode": 201, "message": "Trip data extracted successfully.", "data": trip_data}
    else:
        return resp.raw()
    
"""
Work on Driver endpoints
"""
@app.get("/api/drivers/{driver_id}")
def get_driver(driver_id: int):
    """
    Get driver details by driver ID.
    """
    conn = get_db_connection()
    driver = conn.execute('SELECT * FROM drivers WHERE id = ?', (driver_id,)).fetchone()
    conn.close()
    if driver is None:
        return {"apicode": 404, "message": f"Driver with ID {driver_id} not found."}
    return {"apicode": 200, "data": dict(driver)}

@app.post("/api/drivers/")
def create_driver(name: str, license_number: str, phone: str):
    """
    Create a new driver.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_at = created_at
    cursor.execute('''
        INSERT INTO drivers (name, license_number, phone, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, license_number, phone, created_at, updated_at))
    driver_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"apicode": 201, "message": "Driver created successfully.", "data": {"driver_id": driver_id, "name": name, "license_number": license_number, "phone": phone, "created_at": created_at, "updated_at": updated_at}}

@app.put("/api/drivers/{driver_id}")
def update_driver(driver_id: int, name: Union[str, None] = None, license_number: Union[str, None] = None, phone: Union[str, None] = None):
    """
    Update driver details.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    driver = conn.execute('SELECT * FROM drivers WHERE id = ?', (driver_id,)).fetchone()
    if driver is None:
        conn.close()
        return {"apicode": 404, "message": f"Driver with ID {driver_id} not found."}

    updated_name = name if name is not None else driver['name']
    updated_license_number = license_number if license_number is not None else driver['license_number']
    updated_phone = phone if phone is not None else driver['phone']
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
        UPDATE drivers
        SET name = ?, license_number = ?, phone = ?, updated_at = ?
        WHERE id = ?
    ''', (updated_name, updated_license_number, updated_phone, updated_at, driver_id))
    conn.commit()
    conn.close()
    return {"apicode": 200, "message": "Driver updated successfully.", "data": {"driver_id": driver_id, "name": updated_name, "license_number": updated_license_number, "phone": updated_phone, "updated_at": updated_at}}



@app.get("/api/dashboard")
def get_dashboard():
    """
    Dashboard endpoint providing summary statistics.
    - Total trips
    - Trips by status
    - Total drivers
    - Total trucks
    - Upcoming Trips
    - Recently completed trips
    - Alerts (e.g., delayed trips, maintenance due)
    - Recent activity log
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    total_trips = cursor.execute('SELECT COUNT(*) FROM trips').fetchone()[0]
    total_drivers = cursor.execute('SELECT COUNT(*) FROM drivers').fetchone()[0]
    total_trucks = cursor.execute('SELECT COUNT(*) FROM trucks').fetchone()[0]

    trips_by_status = cursor.execute('SELECT status, COUNT(*) as count FROM trips GROUP BY status').fetchall()
    status_summary = {row['status']: row['count'] for row in trips_by_status}

    return {
        "total_trips": total_trips,
        "total_drivers": total_drivers,
        "total_trucks": total_trucks,
        "trips_by_status": status_summary
    }



"""try:
    conn = get_db_connection()
    conn.execute('SELECT 1')
    activity_logger.info("Database connection successful.")
except Exception as e:
    error_logger.error(f"Database connection failed: {e}")
    sys.exit(1)

resp = extract_from_pdf('/home/tinashe/Desktop/projects/mtl-api/tests/test-data/pdfs/VAR-2001.pdf')

if resp.apicode == 201:
    content = resp.raw()
    text = content['created']['raw_text']
    p = process_pdf_text(text)
    print(p)"""