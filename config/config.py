"""
author: Tinashe Kucherera
date: 2024-06-20
description: This is a resourse for managing the database configuration.
"""

"""
Goals for this module:
- Define the congiration manager for the database.
- Ensure data validation and integrity.
- handle reading and wrting to database
"""

import messages as msg
from datetime import datetime
from logger import activity_logger, stdout_logger

class ConfigManager:
    """
    This is a configuration manager for the database.
    It will handle reading and writing to the database.
    It will also handle data validation and integrity.
    """
    table_name = None
    
    def create(self, conn, props: dict):
        """
        Insert a new row into the database table
        """
        stdout_logger.info(props)
        # remove id from props 
        if 'id' in props:
            props.pop('id')
        cursor = conn.cursor()
        # Example for inserting into a generic table, adjust as needed
        placeholders = ', '.join('?' * len(props))
        columns = ', '.join(props.keys())
        if self.table_name:
            sql = f'INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})'
            cursor.execute(sql, tuple(props.values()))
            conn.commit()

        self.id = cursor.lastrowid
        if self.id is None:
            return msg.ResourceCreateError({'error': 'Failed to create item'})
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return msg.ResourceCreated(self.__dict__)

    @classmethod
    def get(cls,conn, id):
        """
        Read a row from the database table
        returns a single row or None
        """
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {cls.table_name} WHERE id = ?", (id,))
        item = cursor.fetchone()
        if item is None:
            return msg.ResourceNotFound({'id': id})
        return msg.ResourceFound(dict(item))

    @classmethod
    def all(cls, conn):
        """
        Read all rows from the database table
        returns a list of rows or empty list
        """
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {cls.table_name}")
        items = cursor.fetchall()
        if not items:
            return msg.ResourceNotFound({'items': []})
        return msg.ResourceFound([dict(item) for item in items])

        
    @classmethod
    def update(cls, conn, id, **kwargs):
        """
        Update a row in the database table
        returns the updated row or error
        """
        update_args = {key: value for key, value in kwargs.items() if value is not None }
        if not update_args:
            return msg.ResourceUpdateError({'error': 'No properties to update'})
        cursor = conn.cursor()
        columns = ', '.join([f"{key}=?" for key in update_args.keys()])
        sql = f"UPDATE {cls.table_name} SET {columns} WHERE id=?"
        values = list(update_args.values()) + [id]
        cursor.execute(sql, values)
        conn.commit()
        if cursor.rowcount == 0:
            return msg.ResourceUpdateError({'error': 'No row updated', 'id': id})
        resource = cls.get(conn, id).raw()
        if 'found' in resource.keys():
            return msg.ResourceUpdated(resource['found'])
    
    @classmethod
    def filter(cls, conn, **kwargs):
        """
        Query DB and Return rows 

        """
        cursor = conn.cursor()

        query_dict = {key: value for key, value in kwargs.items() if value is not None}
        if not query_dict:
            cursor.execute(f"SELECT * FROM {cls.table_name}")
            items = cursor.fetchall()
        else:
            conditions = ' AND '.join([f"{key}=?" for key in query_dict.keys() ])
            sql = f"SELECT * FROM {cls.table_name} WHERE {conditions}"
            cursor.execute(sql, tuple(query_dict.values()))
            items = cursor.fetchall()
        if not items:
            return msg.ResourceNotFound({'items': []})
        return msg.ResourceFound([dict(item) for item in items])

    def delete():
        """
        Delete a row from the database table
        returns success or error

        ## Note: Deleting is the last thing to support would rather set object as inactive.
        """
        pass