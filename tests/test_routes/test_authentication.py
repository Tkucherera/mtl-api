import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_login_success():
    response = client.post(
        '/api/login',
        data={'username': 'jdoe@gmail.com', 'password': 'WeakPassword'}
    )
    assert response.status_code == 200
    res = response.json()
    assert res['access_token'] is not None

def test_login_fail():
    response = client.post(
        '/api/login',
        data={'username': 'jdoe@gmail.com', 'password': 'Password'}
    )
    assert response.status_code == 401
    

