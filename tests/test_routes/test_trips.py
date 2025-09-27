# tests/test_trips.py

def test_trip_get(client):
    response = client.get('/api/trips/1')
    print(response.json())
    assert response.status_code == 200
    assert response.json()["found"]["id"] == 1
    assert response.json()["found"]["broker"] == "Acme Logistics"


def test_trip_get_filters(client):
    response = client.get('/api/trips/?broker=Global%20Freight')
    assert response.status_code == 200
    trips = response.json()["found"]
    assert len(trips) >= 1
    assert trips[0]["broker"] == "Global Freight"


def test_trip_not_found(client):
    response = client.get('/api/trips/200')
    assert response.status_code == 404
    assert response.json() == {"not found": {"id": 200}}


def test_trip_create(client):
    new_trip = {
        "broker": "Mary Inc",
        "rate_con_number": "RC200",
        "rate": 1500.0,
        "pickup_location": "Greensboro, NC",
        "dropoff_location": "Charlotte, NC",
        "pickup_date": "2025-06-25T10:00:00",
        "delivery_date": "2025-06-30T18:00:00",
        "truck_id": 101
    }
    response = client.post('/api/trips/', json=new_trip)
    assert response.status_code == 201
    ret = response.json()['created']
    assert ret["broker"] == "Mary Inc"
    assert ret["truck_id"] == 101


def test_trip_put(client):
    response = client.put('/api/trips/1/?truck_id=102&&status=Pending%20Pickup')
    assert response.status_code == 200
    ret = response.json()['updated']
    assert ret['truck_id'] == 102
    assert ret['status'] == 'Pending Pickup'

    # rollback for reruns
    response = client.put('/api/trips/1/?truck_id=101&&status=Scheduled')
    ret = response.json()['updated']
    assert ret['truck_id'] == 101
    assert ret['status'] == 'Scheduled'
