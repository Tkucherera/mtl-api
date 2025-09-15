from datetime import datetime
from config.config import ConfigManager
import messages as msg


class Roles:
    'super_user' = 'SUPER'
    'driver' = 'DRIVER'
    'admin' = 'ADMIN'
    'truck_owner' = 'TRUCK OWNER'

class Profile:
    def __init__(self, fname, lname, email, phone, password, profile_picture=None):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.phone = phone
        self.password = password
        self.profile_picture = profile_picture
        


class Driver(ConfigManager, Profile):
    def __init__(self, fname: str, lname: str, phone: str, email: str, password: str, license_number: str, profile_picture=None, pay_rate: float | None = None, status=None):
        self.id = None
        self.license_number = license_number
        self.pay_rate = pay_rate
        self.status = status # this is their employment status 
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Profile.__init__(self,fname, lname, email, phone, password, profile_picture)


class Admin(ConfigManager, Profile):
    def __init__(self, fname: str, lname: str, phone: str, email: str, password: str, profile_picture=None):
        Profile.__init__(self,fname, lname, email, phone, password, profile_picture)

class TruckOwner(ConfigManager, Profile):
    def __init__(self, fname: str, lname: str, phone: str, email: str, password: str, profile_picture=None):
        Profile.__init__(self,fname, lname, email, phone, password, profile_picture)






