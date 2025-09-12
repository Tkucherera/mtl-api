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

class TestTrip(unittest.TestCase):

    def test_trip_initialization(self):
        trip = Trip(
            truck_id=1,
            broker="Broker A",
            rate_con_number="RC123",
            rate=1500.0,
            pickup_location="Location A",
            dropoff_location="Location B",
            pickup_date="2024-06-25",
            delivery_date="2024-06-30"
        )
        trip.create()
        self.assertEqual(trip.truck_id, 1)
        self.assertEqual(trip.broker, "Broker A")
        self.assertEqual(trip.status, LoadStatus.SCHEDULED)
        self.assertIsNotNone(trip.created_at)
        self.assertIsNotNone(trip.updated_at)

    def test_trip_update(self):
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
        trip.create()
        time.sleep(1)  # Ensure updated_at is different

        trip.update_status(LoadStatus.IN_TRANSIT)
        self.assertEqual(trip.status, LoadStatus.IN_TRANSIT)
        self.assertNotEqual(trip.created_at, trip.updated_at)

        trip.upate_delivery_date("2025-07-01T00:00:00")
        self.assertEqual(trip.delivery_date, "2025-07-01T00:00:00")
        self.assertNotEqual(trip.created_at, trip.updated_at)

if __name__ == '__main__':
    unittest.main()