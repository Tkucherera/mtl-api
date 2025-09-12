"""
author: Tinashe Kucherera
date: 2024-06-20
description: Module for managing trip data and operations.
"""
import sys
import os

from datetime import datetime
from messages import *




class Trip:
    def __init__(self, truck_id: int, broker: str, rate_con_number: str, rate: float, pickup_location: str, dropoff_location: str, pickup_date: datetime, delivery_date: datetime, status: str = LoadStatus.SCHEDULED):
        self.truck_id = truck_id
        self.broker = broker
        self.rate_con_number = rate_con_number
        self.rate = rate
        self.pickup_location = pickup_location
        self.dropoff_location = dropoff_location
        self.pickup_date = pickup_date
        self.delivery_date = delivery_date
        self.status = status
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.validate_status()
    
    def create(self):
        # Here we would normally save to a database
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return ResourceCreated(self.__dict__)


    def validate_status(self):
        if self.status not in vars(LoadStatus).values():
            raise ValueError(LoadStatusError(self.truck_id, self.status).message)
        
        # in the future we can add more validation rules here
        # e.g. status transitions, permissions, etc.

    def update_status(self, new_status: str):

        if new_status in vars(LoadStatus).values():
            self.status = new_status
            self.updated_at = datetime.now()
            return ResourceUpdated(self.__dict__)
        else:
            raise ValueError(LoadStatusError(self.truck_id, new_status).message)

    
    def upate_delivery_date(self, new_delivery_date: datetime):
        self.delivery_date = new_delivery_date
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return ResourceUpdated(self.__dict__)


