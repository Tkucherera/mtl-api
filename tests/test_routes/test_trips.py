import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_trip_get():
    response = client.get('/api/trips/1')
    assert response.status_code == 200
    assert response.json() == {"found":{"id":1,"truck_id":2,"broker":"Tinashe Inc","rate_con_number":"RC123","rate":1500.0,"pickup_location":"Location A","dropoff_location":"Location B","pickup_date":"2024-06-25T10:00:00","delivery_date":"2024-06-30T18:00:00","status":"Scheduled","created_at":"2025-09-13 19:03:07","updated_at":"2025-09-13 19:03:07","driver_id":None}}

def test_trip_get_filters():
    response = client.get('/api/trips/?broker=Tinashe%20Inc')
    assert response.status_code == 200
    assert response.json() == {"found":[{"id":1,"truck_id":2,"broker":"Tinashe Inc","rate_con_number":"RC123","rate":1500.0,"pickup_location":"Location A","dropoff_location":"Location B","pickup_date":"2024-06-25T10:00:00","delivery_date":"2024-06-30T18:00:00","status":"Scheduled","created_at":"2025-09-13 19:03:07","updated_at":"2025-09-13 19:03:07","driver_id":None}]}

def test_trip_not_found():
    response = client.get('/api/trips/200')
    assert response.status_code == 404
    assert response.json() == {"not found": {"id": 200}}

def test_trip_create():
    new_trip = {
        "broker":"Mary Inc",
        "rate_con_number":"RC136",
        "rate":1500.0,
        "pickup_location":"3562 Hewitt St Greensboro, NC",
        "dropoff_location":"170 Glenwood Ave, Raleigh, NC",
        "pickup_date":"2025-06-25T10:00:00",
        "delivery_date":"2025-06-30T18:00:00",
        "truck_id":1
    }
    response =  client.post('/api/trips/', json=new_trip)
    assert response.status_code == 201
    ret = response.json()['created']
    assert ret['broker'] == new_trip["broker"]
    assert ret["delivery_date"] == new_trip["delivery_date"]
    assert ret["rate_con_number"] == new_trip["rate_con_number"]
    assert ret["rate"] == new_trip["rate"]
    assert ret["dropoff_location"] == new_trip["dropoff_location"]
    assert ret["pickup_date"] == new_trip["pickup_date"]
    assert ret["pickup_location"] == new_trip["pickup_location"]
    assert ret['status'] is not None
    assert ret['updated_at'] is not None
    assert ret['created_at'] is not None

def test_trip_put():
    trip = {
            'broker': 'Mary Inc',
            'created_at': '2025-09-16 00:57:22',
            'delivery_date': '2025-06-30T18:00:00',
            'driver_id': None,
            'dropoff_location': '170 Glenwood Ave, Raleigh, NC',
            'pickup_date': '2025-06-25T10:00:00',
            'pickup_location': '3562 Hewitt St Greensboro, NC',
            'rate': 1500.0,
            'rate_con_number': 'RC136',
            'status': 'Scheduled',
            'trip_id': 7,
            'truck_id': 1,
            'updated_at': '2025-09-16 00:57:22',
        }
    # update trip 
    response = client.put('/api/trips/7/?truck_id=2&&status=Pending%20Pickup')
    assert response.status_code == 200
    ret = response.json()['updated']
    assert ret['truck_id'] == 2
    assert ret['status'] == 'Pending Pickup'

    # change back for reruns
    response = client.put('/api/trips/7/?truck_id=1&&status=Scheduled')
    ret = response.json()['updated']
    assert ret['truck_id'] == 1
    assert ret['status'] == 'Scheduled'




    
    



