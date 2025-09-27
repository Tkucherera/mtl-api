from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from jwt import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from config.db import get_db_session
from models import Profile, Driver  # ORM models
from schemas import ProfileOut, DriverOut  # Pydantic schemas

# ======================================================
# Settings
# ======================================================
SECRET_KEY = "a96e5a47ac3b6020a9d36f8fc715b641d6e3f6c592d59c904c0f9530b38c3696"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# ======================================================
# Password hashing (Argon2)
# ======================================================
ph = PasswordHasher(time_cost=3, memory_cost=64*1024, parallelism=2, hash_len=32)

def get_password_hash(password: str) -> str:
    """Hash a password using Argon2."""
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the hashed password."""
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False

# ======================================================
# JWT token creation
# ======================================================
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token with expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ======================================================
# Authentication
# ======================================================
def authenticate_user(db: Session, email: str, password: str) -> Profile | None:
    """Return the user if credentials are correct, otherwise None."""
    user: Profile | None = db.query(Profile).filter(Profile.email == email).first()
    if not user or not verify_password(password, user.password):
        return None
    return user

# ======================================================
# Token decoding helper
# ======================================================
def _decode_token(token: str) -> str:
    """Decode JWT and return the email (sub). 
       # TODO Issue new token if token about to expire
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return email
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ======================================================
# Dependencies
# ======================================================
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db_session)
) -> ProfileOut:
    """Return current logged-in user (ProfileOut schema)."""
    email = _decode_token(token)
    user: Profile | None = db.query(Profile).filter(Profile.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return ProfileOut.model_validate(user)

async def get_current_driver(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db_session),
) -> DriverOut:
    """Return current logged-in driver with nested profile (DriverOut schema)."""
    user: Profile = await get_current_user(token, db)
    driver: Driver | None = db.query(Driver).filter(Driver.profile_id == user.id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    return DriverOut.model_validate(driver)

