"""
author: Tinashe Kucherera
date: 2024-06-20
description: To make sure messages are consistent across the application for web, mobile and desktop.

"""

"""
This will help us maintain consistency in the messages shown to users across different platforms.
it will contain the structure of the messages and their content. from http responses, json and terminal.
"""

import json


class MTLMessage:
    """
    Base class for messages.
    """
    apicode = 200
    read_only = False
    default_value = ''
    default_type = str

    def __init__(self,):
        self.desc = ''
        self.kvargs = {}
    
    def to_json(self):

        return json.dumps(self.kvargs, sort_keys=True)
    
    def raw(self):
        return self.kvargs
    
    def html(self):
        return f"""
        <html>
            <head><title>Message {self.apicode}</title></head>
            <body>
                <h1>Message {self.apicode}</h1>
                <p>{self.kvargs.get('message', '')}</p>
            </body>
        </html>
        """
    
class MTLError:
    apicode = 400

    def __init__(self, error: dict):
        self.args = [error]
        self.desc = "Error"
        self.kvargs = { 'error': error, 'error_code': self.apicode}



    def to_json(self):
        return json.dumps(self.kvargs, sort_keys=True)
    
    def raw(self):
        return self.kvargs
    
    def html(self):
        return f"""
        <html>
            <head><title>Error {self.apicode}</title></head>
            <body>
                <h1>Error {self.apicode}</h1>
                <p>{self.kvargs.get('error', '')}</p>
            </body>
        </html>
        """
    
class ResourceCreateError(MTLError):
    apicode = 500
    def __init__(self, error: dict):
        self.args = [error]
        self.desc = "Resource Creation Error"
        self.kvargs = { 'error': error, 'error_code': self.apicode}


    
        

class ResourceCreated(MTLMessage):
    apicode = 201

    def __init__(self, resource: dict):
        self.args = [resource]
        self.desc = "Create Resource"
        self.kvargs = { 'created': resource}

class ResourceUpdated(MTLMessage):
    apicode = 200

    def __init__(self, resource: dict):
        self.args = [resource]
        self.desc = "Update Resource"
        self.kvargs = { 'updated': resource}

class ResourceDeleted(MTLMessage):
    apicode = 200

    def __init__(self, resource:dict):
        self.args = [resource]
        self.desc = "Delete Resource"
        self.kvargs = { 'deleted': resource}

class ResourceFound(MTLMessage):
    apicode = 200

    def __init__(self, resource: dict):
        self.args = [resource]
        self.desc = "Resource Found"
        self.kvargs = { 'found': resource}

class ResourceNotFound(MTLMessage):
    apicode = 404

    def __init__(self, resource: dict):
        self.args = [resource]
        self.desc = "Resource Not Found"
        self.kvargs = { 'not found': resource}

class ResourceCreateError(MTLError):
    apicode = 400

    def __init__(self, error: dict):
        self.args = [error]
        self.desc = "Resource Error"
        self.kvargs = { 'error': error} 

class ResourceUpdateError(MTLError):
    apicode = 400

    def __init__(self, error: dict):
        self.args = [error]
        self.desc = "Resource Update Error"
        self.kvargs = { 'error': error, 'error_code': self.apicode }


class LoadStatus:
    SCHEDULED = "Scheduled"
    PENDING = "Pending Pickup" 
    LOADED = "Loaded"
    IN_TRANSIT = "In Transit"
    LOADED_OUT = "Loaded Out"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"

class LoadStatusError:
    """
    Error message for invalid load status.
    This may happen for the following reasons:
    - The status provided is not one of the predefined statuses.
    - The status transition is not allowed (cannot go from not pickup to delivered) maybe permissions issue wont enforce for now . 

    """
    apicode = 400

    def __init__(self, trip_id, status: str):
        self.status = status
        self.trip_id = trip_id
        self.message = f"Invalid load status: {status}. Allowed statuses are: {', '.join(vars(LoadStatus).values())}"

    def to_json(self):
        return json.dumps({
            "trip_id": self.trip_id,
            "status": self.status,
            "message": self.message,
            "code": self.apicode
        })
    
    def raw(self):
        return {
            "trip_id": self.trip_id,
            "status": self.status,
            "message": self.message,
            "code": self.apicode
        }
    
    def html(self):
        return f"""
        <html>
            <head><title>Error {self.apicode}</title></head>
            <body>
                <h1>Error {self.apicode}</h1>
                <p>Trip ID: {self.trip_id}</p>
                <p>Status: {self.status}</p>
                <p>Message: {self.message}</p>
            </body>
        </html>
        """
   

