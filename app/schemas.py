from datetime import date, time, datetime
from typing import Dict, Literal, Optional, List
from psycopg2 import Time
from pydantic import BaseModel, EmailStr, Field, HttpUrl, constr, validator
from pydantic.types import conint
from fastapi import File, UploadFile

class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    created_at: datetime
    
    
    class Config:
        from_attributes = True
class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    id: Optional[int] = None

class userAppend(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    class Config:
        from_attributes = True
    

class imageVerification(BaseModel):
    id: int
    user_id: int
    user: userAppend
    # image: None
    image_mime: Optional[str]
    # image_url: str
    created_at: datetime
    class Config:
        from_attributes = True
    
class ImageOut(BaseModel):
    id: int
    user_id: int
    user: userAppend
    created_at: datetime
    image_url: str | None = None

    class Config:
        from_attributes = True
  
class getImage(imageVerification):
    name: str
    email: str
    

class TicketBase(BaseModel):
    name: str
    price: float = 0.0
    currency: Literal["NGN", "USD"] = "NGN"
    quantity_total: int
    per_person_limit: Optional[int] = None
    is_seat_based: bool = False

class TicketCreate(TicketBase):
    event_id: int

class TicketOut(TicketBase):
    id: int
    event_id: int
    quantity_sold: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Invite Schemas ----------
class EventInviteBase(BaseModel):
    user_id: Optional[int] = None  # null = not registered yet

class EventInviteCreate(EventInviteBase):
    event_id: int

class EventInviteOut(EventInviteBase):
    id: int
    event_id: int
    status: Literal["pending", "accepted", "declined"]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Order Schemas ----------
class OrderBase(BaseModel):
    quantity: int
    amount_paid: float
    payment_status: Literal["pending", "paid", "failed"] = "pending"
    paystack_reference: Optional[str] = None

class OrderCreate(OrderBase):
    user_id: int
    event_id: int
    ticket_id: int

class OrderOut(OrderBase):
    id: int
    user_id: int
    event_id: int
    ticket_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class EventBase(BaseModel):
        title: str
        description: str
        category: str
        start_date: date
        end_date: Optional[date] = None
        start_time: str
        location: Optional[str] = None
        capacity: int
        visibility: str
        image_url: Optional[str] = None
        image_file: Optional[UploadFile] = None
        image_mime: Optional[str] = None
        
        @validator('start_date', 'end_date', pre=True)
        def parse_custom_date(cls, value):
            if value is None:
                return value
            if isinstance(value, date):
                return value
            try:
                return datetime.strptime(value, "%d/%m/%Y").date()
            except ValueError:
                raise ValueError("Date must be in DD/MM/YYYY format")
            
    
class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    capacity: Optional[int] = None
    visibility: Optional[Literal["public", "private"]] = None
    image_url: Optional[str] = None     
    image_file: Optional[bytes] = None  
    image_mime: Optional[str] = None

class EventOut(BaseModel):
    id: int
    organizer_id: int
    organizer: userAppend
    title: str
    description: str
    category: str
    location: str
    start_date: date
    end_date: Optional[date] 
    start_time: time
    end_time: Optional[time]
    capacity: Optional[int]
    visibility: str
    event_link: Optional[str]
    invite_token: Optional[str]
    # invite_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    image_url: Optional[str] = None     
    image_data: Optional[bytes] = None  
    image_mime: Optional[str] = None
    class Config:
        from_attributes = True
             


class EventDetail(EventOut):
    tickets: List[TicketOut] = []
    invites: List[EventInviteOut] = []
    
class EventInviteToken(BaseModel):
    invite_token: str
    invite_url: str