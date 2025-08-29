from datetime import datetime
from typing import Dict, Optional, List
from pydantic import BaseModel, EmailStr, HttpUrl
from pydantic.types import conint

class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime
    image: Optional[str]  
    image_mime: Optional[str]
    image_url: Optional[str] = None 
    
    class config:
        orm = True
    
    
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    password: str
    confirm_password: str


class UserProfile(BaseModel):
    name: str
    email: str
    phone_number: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    id: Optional[int] = None


