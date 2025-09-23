import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from config.config import ConfigManager
from config.db import get_db_connection
import messages as msg
from pydantic import BaseModel
from users.utils import secure_password


class DriverItem(BaseModel):
    fname: str
    lname: str
    email: str
    phone: str
    password: str
    license_number: str
    pay_rate: float
    status: str
    profile_picture: str = None

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
    def get_user_by_email(cls,conn, email):
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
    


    


class Admin(Profile):
    def __init__(self, fname: str, lname: str, phone: str, email: str, password: str, profile_picture=None):
        Profile.__init__(self,fname, lname, email, phone, password, profile_picture)

class TruckOwner(Profile):
    def __init__(self, fname: str, lname: str, phone: str, email: str, password: str, profile_picture=None):
        Profile.__init__(self,fname, lname, email, phone, password, profile_picture)


