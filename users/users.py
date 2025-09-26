import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from config.config import ConfigManager
from config.db import get_db_connection
import messages as msg
from pydantic import BaseModel
from users.utils import secure_password




class Roles:
    super_user = 'SUPER'
    driver = 'DRIVER'
    admin = 'ADMIN'
    truck_owner = 'TRUCK OWNER'


class LoginItem(BaseModel):
    email: str
    password: str




class Profile(ConfigManager):
    table_name = 'profiles'
    def __init__(self, fname, lname, email, phone, password, profile_picture=None):
        self.id = None
        self.fname = fname
        self.lname = lname
        self.email = email
        self.phone = phone
        self.password = secure_password(password)
        self.profile_picture = profile_picture

    def create_user(self, conn):
        # check db if some of the values that should be unique are 
        # check if email already in db 
        check=self.filter(conn, email=self.email, phone=self.phone)
        if type(check) is msg.ResourceFound:
            raise Exception('profile with email or phone already exists')
        res= self.create(conn, self.__dict__)
        if res.apicode == 400:
            raise Exception(res)
        return res.raw()
    
    @classmethod
    def get_user_by_email(cls,conn, email: str) -> msg.ResourceFound | msg.ResourceNotFound:
        """
        Read a row from the database table
        returns a single row or None
        """
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {cls.table_name} WHERE email = ?", (email,))
        item = cursor.fetchone()
        if item is None:
            return msg.ResourceNotFound({'email': email})
        return msg.ResourceFound(dict(item))
    
    @classmethod
    def get_user_id(cls, conn, email: str) -> int | None:
        """
        Read a row from the database table
        returns id 
        """
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM {cls.table_name} WHERE email = ?", (email,))
        item = cursor.fetchone()
        if item is None:
            return None
        return item['id'] if 'id' in item else item[0]
    
class ProfileItem(BaseModel):
    id: int
    fname: str
    lname: str
    email: str
    phone: str
    password: str | None 
    profile_picture: str | None = None
        


class DriverItem(BaseModel):
    profile: ProfileItem
    license_number: str
    pay_rate: float
    status: str
    id: int
    profile_id: int


class Driver(ConfigManager):
    table_name = 'drivers'
    fields = ['id', 'license_number', 'pay_rate', 'status', 'created_at', 'updated_at', 'profile_id']
    def __init__(self, profile: Profile, license_number: str, pay_rate: float | None = None, status=None):
        self.id = None
        self.license_number = license_number
        self.pay_rate = pay_rate
        self.status = status # this is their employment status 
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.profile = profile
        self.profile_id = profile.id

    # idea here it that calling create method should create the profile first then driver
    def create_driver(self, conn):
        if self.profile.id is None:
            res = self.profile.create_user(conn)
            if 'created' in res:
                self.profile.id = res['created']['id']
                self.profile_id = self.profile.id

        props = {k: getattr(self, k) for k in self.fields}
        return self.create(conn, props)
    
    @classmethod
    def get_driver_by_profile_id(cls, conn, id):
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {cls.table_name} WHERE profile_id = ?", (id,))
        item = cursor.fetchone()
        if item is None:
            return msg.ResourceNotFound({'profile_id': id})
        return msg.ResourceFound(dict(item))
    
    @classmethod
    def get_driver_trips(cls, conn, id):
        """
        Returns all trips for a given driver (by profile_id).
        """
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM trips WHERE driver_id = ? ORDER BY start_time DESC",
            (id,)
        )
        items = cursor.fetchall()
        if not items:
            return msg.ResourceNotFound({'driver_id': id})
        return msg.ResourceFound([dict(item) for item in items])

    @classmethod
    def get_driver_current_trip(cls, conn, id):
        """
        Returns the current (active) trip for a given driver (by profile_id).
        """
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM trips WHERE driver_id = ? AND status = ? ORDER BY start_time DESC LIMIT 1",
            (id, 'ACTIVE')
        )
        item = cursor.fetchone()
        if item is None:
            return msg.ResourceNotFound({'driver_id': id, 'status': 'ACTIVE'})
        return msg.ResourceFound(dict(item))

    @classmethod
    def get_driver_miles(cls, conn, id):
        """
        Returns the total miles driven by a driver (by profile_id).
        """
        cursor = conn.cursor()
        cursor.execute(
            "SELECT SUM(distance) as total_miles FROM trips WHERE driver_id = ?",
            (id,)
        )
        item = cursor.fetchone()
        total_miles = item['total_miles'] if item and item['total_miles'] is not None else 0
        return total_miles

    @staticmethod
    def calculate_driver_fee(tripitem, driver_rate: float):
        """
        Calculates the driver's fee for a trip.
        Assumes tripitem has a 'distance' field.
        """
        distance = tripitem.get('distance', 0)
        return distance * driver_rate



    


class Admin(Profile):
    def __init__(self, fname: str, lname: str, phone: str, email: str, password: str, profile_picture=None):
        Profile.__init__(self,fname, lname, email, phone, password, profile_picture)

class TruckOwner(Profile):
    def __init__(self, fname: str, lname: str, phone: str, email: str, password: str, profile_picture=None):
        Profile.__init__(self,fname, lname, email, phone, password, profile_picture)


