"""
author: Tinashe Kucherera
date: 2024-06-20
description: Using SQLite for lightweight, as we go might migrate to a more robust DB.
Database configuration and initialization.
"""

import sqlite3


def get_db_connection(testing: bool = False):
    if testing:
        connection = sqlite3.connect(':memory:')
    else:
        connection = sqlite3.connect('mtl.db')
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    return connection

connection = get_db_connection()
cursor = connection.cursor()

# Create trips table
cursor.execute('''
CREATE TABLE IF NOT EXISTS trips (
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
''')

# Create drivers table
cursor.execute('''
CREATE TABLE IF NOT EXISTS drivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    license_number TEXT NOT NULL,
    phone TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
''')