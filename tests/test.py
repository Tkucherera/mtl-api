"""
author: Tinashe Kucherera
date: 2024-06-20
description: Running tests for server side application.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from services.trip import Trip
from messages import *
import time
import sqlite3

class TestTrip(unittest.TestCase):

    def setUp(self):
        # Fresh in-memory DB for each test
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        # Create schema
        cursor.execute("""
        CREATE TABLE trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            truck_id INTEGER NOT NULL,
            broker TEXT NOT NULL,
            rate_con_number TEXT NOT NULL,
            rate REAL NOT NULL,
            pickup_location TEXT NOT NULL,
            dropoff_location TEXT NOT NULL,
            pickup_date TEXT NOT NULL,
            delivery_date TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            driver_id INTEGER,
            FOREIGN KEY (driver_id) REFERENCES drivers(id)
        )
        """)

    def tearDown(self):
        self.conn.close()

    def test_trip_initialization(self):
        trip = Trip(
            truck_id=1,
            broker="Broker A",
            rate_con_number="RC123",
            rate=1500.0,
            pickup_location="Location A",
            dropoff_location="Location B",
            pickup_date="2024-06-25T10:00:00",
            delivery_date="2024-06-30T18:00:00"
        )
        self.assertEqual(trip.broker, "Broker A")
        self.assertEqual(trip.rate_con_number, "RC123")
        self.assertEqual(trip.rate, 1500.0)
        self.assertEqual(trip.pickup_location, "Location A")
        self.assertEqual(trip.dropoff_location, "Location B")
        self.assertEqual(trip.pickup_date, "2024-06-25T10:00:00")
        self.assertEqual(trip.delivery_date, "2024-06-30T18:00:00")
        self.assertEqual(trip.status, LoadStatus.SCHEDULED)
        self.assertIsNone(trip.driver_id)
        self.assertIsNotNone(trip.truck_id)


    def test_get_trips(self):
        conn = self.conn
        cursor = conn.cursor()
        cursor.execute('DELETE FROM trips')  # Clear existing data
        conn.commit()


        trip1 = Trip(
            truck_id=1,
            broker="Broker A",
            rate_con_number="RC123",
            rate=1500.0,
            pickup_location="Location A",
            dropoff_location="Location B",
            pickup_date="2024-06-25T10:00:00",
            delivery_date="2024-06-30T18:00:00"
        )
        trip2 = Trip(
            truck_id=2,
            broker="Broker B",
            rate_con_number="RC456",
            rate=2000.0,
            pickup_location="Location C",
            dropoff_location="Location D",
            pickup_date="2024-07-01T09:00:00",
            delivery_date="2024-07-05T17:00:00"
        )
        res1 = trip1.create(conn, trip1.__dict__)
        res2 = trip2.create(conn, trip2.__dict__)
        self.assertEqual(res1.apicode, 201)
        self.assertEqual(res2.apicode, 201)

        cursor.execute('SELECT * FROM trips')
        trips = cursor.fetchall()
        self.assertEqual(len(trips), 2)

        conn.close()
    def test_update_trip_status(self):
        conn = self.conn
        cursor = conn.cursor()
        cursor.execute('DELETE FROM trips')  # Clear existing data
        conn.commit()

        trip = Trip(
            truck_id=1,
            broker="Broker A",
            rate_con_number="RC123",
            rate=1500.0,
            pickup_location="Location A",
            dropoff_location="Location B",
            pickup_date="2024-06-25T10:00:00",
            delivery_date="2024-06-30T18:00:00"
        )
        res = trip.create(conn, trip.__dict__)
        self.assertEqual(res.apicode, 201)
        trip_id = res.raw()['created']['trip_id']

        # Update status to IN_TRANSIT
        res_update = Trip.update_status(trip_id, LoadStatus.IN_TRANSIT, conn)
        self.assertEqual(res_update.apicode, 200)

        # Verify update
        cursor.execute('SELECT status FROM trips WHERE id = ?', (trip_id,))
        updated_trip = cursor.fetchone()
        self.assertEqual(updated_trip['status'], LoadStatus.IN_TRANSIT)

        conn.close()

class TestMessages(unittest.TestCase):

    def test_mtl_message(self):
        msg = MTLMessage()
        msg.kvargs = {'message': 'Test message'}
        self.assertEqual(msg.apicode, 200)
        self.assertIn('Test message', msg.to_json())
        self.assertIn('Test message', msg.html())

    def test_mtl_error(self):
        error_info = {'detail': 'Not found'}
        err = MTLError(error_info)
        self.assertEqual(err.apicode, 400)
        self.assertIn('Not found', err.to_json())
        self.assertIn('Not found', err.raw()['error']['detail'])
        self.assertIn('Not found', err.html())

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            truck_id INTEGER NOT NULL,
            broker TEXT NOT NULL,
            rate_con_number TEXT NOT NULL,
            rate REAL NOT NULL,
            pickup_location TEXT NOT NULL,
            dropoff_location TEXT NOT NULL,
            pickup_date TEXT NOT NULL,
            delivery_date TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            driver_id INTEGER,
            FOREIGN KEY (driver_id) REFERENCES drivers(id)
        )
        """)
        cursor.execute("""
        CREATE TABLE drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            license_number TEXT,
            phone TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """)
        self.conn.commit()
    
    def tearDown(self):
        self.conn.close()

    def test_db_connection(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        self.assertEqual(result[0], 1)
        self.conn.close()

    def test_db_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table['name'] for table in tables]
        self.assertIn('trips', table_names)
        self.assertIn('drivers', table_names)
        self.conn.close()

if __name__ == '__main__':
    unittest.main()


# Missing Coverage 
"""
1. Updating Load Status and Validating Updating 
2. Validating filters 
3. Validate update process 
4. 
"""