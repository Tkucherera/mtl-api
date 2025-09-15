"""
author: Tinashe Kucherera
date: 2024-06-20
description: Module for managing truck data and operations.
"""

import sys
import os
from datetime import datetime
import messages as msg
from config.config import ConfigManager

"""
Goals for this module:
- Define a Truck class to represent truck entities.
- Implement methods for truck operations (e.g., get truck info).
- Ensure data validation and integrity.
- Functionality to associate trucks with trips and drivers.
- Fucntions to know truck availability based on trip schedules.
- Fucntions to update truck status (e.g., in service, under maintenance).
- Functions for knowing truck history (past trips, maintenance records).
- Functions to update truck location (if GPS data is available).
- Integration with database for persistent storage.

"""

class Truck(ConfigManager):
    def __init__(self, license_plate: str, model: str, year: int, location=None):
        self.id = None
        self.license_plate = license_plate
        self.model = model
        self.year = year
        self.location = location # This for now doesnt need to be updated every second but maybe every hour or so will probrably use in memory db for per minute or less update
        self.status = "active"  # could be active, inactive, maintenance, available
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    

    


def check_truck_availability(truck_id: int, start_date: datetime, end_date: datetime, conn):
    # This is a placeholder function. Actual implementation would involve checking the trips table
    # for any trips that overlap with the given date range for the specified truck.
    # For now, we'll assume all trucks are available.
    return msg.ResourceFound({'truck_id': truck_id, 'available': True})
# TODO Implement truck availability check based on trip schedules