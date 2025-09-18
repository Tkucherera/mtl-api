"""
author: Tinashe Kucherera
date: 2024-06-20
description: Module for managing trip data and operations.
"""
import sys
import os

from datetime import datetime
import messages as msg
import sqlite3
from config.config import ConfigManager
from pydantic import BaseModel


"""
Goals for this module:
- Define a Trip class to represent trip entities.
- Implement methods for trip operations (e.g., create trip, update status).
- Ensure data validation and integrity.
- Functionality to associate trips with trucks and drivers.
- Functions to track trip status (e.g., scheduled, in transit, delivered).
- Functions to update trip details (e.g., delivery date, pickup location).
- Integration with database for persistent storage.
- Trip history and reporting functions.
- Trip details for specific trip
"""

class TripItem(BaseModel):
    """
    This is an item used to create new trip from client
    """
    broker: str
    rate_con_number: str
    rate: float
    pickup_location: str
    dropoff_location: str
    pickup_date: str
    delivery_date: str
    status: str = msg.LoadStatus.SCHEDULED 
    truck_id: int 
    driver_id: int | None = None
    


class Trip(ConfigManager):
    table_name = 'trips'
    
    def __init__(self, broker: str, rate_con_number: str, rate: float, pickup_location: str, dropoff_location: str, pickup_date: datetime, delivery_date: datetime, truck_id, status: str = msg.LoadStatus.SCHEDULED):
        self.id = None  # This would be set when saved to a database
        self.broker = broker
        self.rate_con_number = rate_con_number
        self.rate = rate
        self.pickup_location = pickup_location
        self.dropoff_location = dropoff_location
        self.pickup_date = pickup_date
        self.delivery_date = delivery_date
        self.status = status
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.driver_id = None
        self.truck_id = truck_id
        self.validate_status()

    def validate_status(self):
        if self.status not in vars(msg.LoadStatus).values():
            raise ValueError(msg.LoadStatusError(self.truck_id, self.status).message)
        
        # in the future we can add more validation rules here
        # e.g. status transitions, permissions, etc.
    @classmethod
    def update_status(cls, trip_id: int, new_status: msg.LoadStatus, conn):
        trip = Trip.get(conn, trip_id)
        if trip.apicode != 200:
            return trip

        if new_status in vars(msg.LoadStatus).values():
            conn.execute('UPDATE trips SET status = ?, updated_at = ? WHERE id = ?', (new_status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), trip_id))
            return msg.ResourceUpdated({'trip_id': trip_id, 'new_status': new_status})
        else:
            raise ValueError(msg.LoadStatusError(trip_id, new_status).message)



class TripHistory:
    """Class to manage trip history, truck, driver, and status changes."""
    def __init__(self, trip_id: int):
        self.trip_id = trip_id
        self.history = []  # This would normally be populated from a database

    def add_history_entry(self, entry: dict):
        entry['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append(entry)
        return msg.ResourceUpdated({'trip_id': self.trip_id, 'history_entry': entry})

    def get_history(self):
        return msg.ResourceFound({'trip_id': self.trip_id, 'history': self.history})
    
class TripDetails:
    """Class to update fetch detailed information about a specific trip."""
    def __init__(self, trip_id: int, driver_id):
        self.trip_id = trip_id
        self.driver = driver_id
        self.miles = 0
        self.deadhead_miles = 0
        self.actual_rate = 0.0
        self.fuel_used = 0.0
        self.expenses = []
        self.payments = []
        self.notes = ""
        self.status_changes = []
        self.driver_changes = []
        self.truck_changes = []
        self.created_at = None
        self.updated_at = None
        self.details = {}  # This would normally be populated from a database

    def calculate_total_expenses(self):
        return sum(expense['amount'] for expense in self.expenses)
    
    def calculate_deadhead_miles(self):
        """
        we need the trip route and then the trip for the next trip
        to calculate the deadhead miles
        """
        self.deadhead_miles = self.miles * 0.1  # Assume 10% of total miles are deadhead
        return self.deadhead_miles
    


def validate_pickup_dropoff():
    """
    Function for determing where the drop off is and pick up 
    Calculate the miles and do more stuff as we need
    """


