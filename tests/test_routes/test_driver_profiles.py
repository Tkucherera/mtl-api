import sys
import os
import json
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_driver_get():
    response = client.get('/api/drivers/1')
    assert response.status_code == 200
    ret = response.json()
    print(ret)
   

def test_driver_not_found():
    response = client.get('/api/drivers/200')
    assert response.status_code == 404
    assert response.json() == {"not found": {"id": 200}}

def test_driver_create():

    new_driver = {
        'fname': 'Jon',
        'lname': 'Doe',
        'email': 'jdoe@email.com',
        'phone': '+1 984 292 2674',
        'password': 'WeakPassword',
        'license_number': 'XX00000',
        'pay_rate': 0.2,
        'status': 'active',
    }
    response =  client.post('/api/drivers/', json=new_driver)
    assert response.status_code == 200
    ret = response.json()['created']
    profile = ret['profile']
    assert profile['fname'] == new_driver["fname"]
    assert profile["lname"] == new_driver["lname"]
    assert profile["email"] == new_driver["email"]
    assert profile["phone"] == new_driver["phone"]
    assert ret["license_number"] == new_driver["license_number"]
    assert ret["status"] == new_driver["status"]
    assert ret['updated_at'] is not None
    assert ret['created_at'] is not None





    
    