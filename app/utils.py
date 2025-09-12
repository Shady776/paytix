from datetime import datetime, timedelta
from tkinter import S
from passlib.context import CryptContext
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def generate_invite_token(length: int = 16, expiry_hours=24):
    token = secrets.token_urlsafe(length)
    # expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
    return  token

def generate_event_token(length: int = 16, expiry_hours=24):
    token = secrets.token_urlsafe(length)
    # expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
    return  token
