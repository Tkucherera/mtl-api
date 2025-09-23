import scrypt
import os
from datetime import datetime, timedelta, timezone

from typing import Annotated 
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt
from jwt.exceptions import InvalidTokenError

from .users import DriverItem, Profile


SECRET_KEY = "a96e5a47ac3b6020a9d36f8fc715b641d6e3f6c592d59c904c0f9530b38c3696"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def secure_password(password, datalength=64, maxtime=0.5):
    return scrypt.encrypt(os.urandom(datalength), password, maxtime=maxtime)


def verify_password(hashed_password, guessed_password, maxtime=0.5):
    """Verify a password against its hash with better error handling.

    Args:
        hashed_password: The stored password hash from hash_password()
        guessed_password: The password to verify
        maxtime: Maximum time to spend in verification

    Returns:
        tuple: (is_valid, status_code) where:
            - is_valid: True if password is correct, False otherwise
            - status_code: One of "correct", "wrong_password", "time_limit_exceeded",
              "memory_limit_exceeded", or "error"

    Raises:
        scrypt.error: Only raised for resource limit errors, which you may want to
                    handle by retrying with higher limits or force=True
    """
    try:
        scrypt.decrypt(hashed_password, guessed_password, maxtime, encoding=None)
        return True, "correct"
    except scrypt.error as e:
        # Check the specific error message to differentiate between causes
        error_message = str(e)
        if error_message == "password is incorrect":
            # Wrong password was provided
            return False, "wrong_password"
        elif error_message == "decrypting file would take too long":
            # Time limit exceeded
            raise  # Re-raise so caller can handle appropriately
        elif error_message == "decrypting file would take too much memory":
            # Memory limit exceeded
            raise  # Re-raise so caller can handle appropriately
        else:
            # Some other error occurred (corrupted data, etc.)
            return False, "error"
        
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None 


def authenticate_user(conn, username, password):
    user = Profile.get_user_by_email(conn, username)
    user_info = user.get('found')
    if user.apicode != 200 and user_info is None:
        return False
    
    hashed_password = user_info.get('password')
    is_valid, status = verify_password(hashed_password, password)
    if not is_valid and status != 'correct':
        return False
    
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(conn, token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exeption = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not valitade user with given credentials',
        headers={"WWW-Authenticate": 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exeption
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exeption
    user = Profile.get_user_by_email(conn=conn, email=token_data.username)
    if user.apicode != 200:
        raise credentials_exeption
    return user



        





