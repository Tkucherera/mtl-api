import os
import scrypt

def secure_password(password, datalength=64, maxtime=0.5):
    return scrypt.encrypt(os.urandom(datalength), password, maxtime=maxtime)

