"""
author: Tinashe Kucherera
date: 2024-06-20
description: This is a resourse to act as gateway between the FastAPI app and the backend of our app.
"""


"""
Goals for this module:
- Manage CRUD operations for clients.
- Ensure data validation and integrity.
- Integration with database for persistent storage.
- Client authentication and authorization (if needed).
- Client details for specific client

"""

class Client(object):
    http_methods = {
        'create': 'POST',
        'read': 'GET',
        'update': 'PUT',
        'delete': 'DELETE'
    }

    def __init__(self):
        pass
    

    def create(self):
        pass

    def read(self):

        pass

    def update(self):
        pass

    def delete(self):
        pass


