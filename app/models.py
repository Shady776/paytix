from pydantic import HttpUrl
from .database import Base
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, LargeBinary, DECIMAL, Boolean, Text, Enum, Time
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
import enum

class VisibilityEnum(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"

class InviteStatusEnum(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')) 
    # image = Column(LargeBinary, nullable=False)
    # image_mime = Column(String, nullable=False)
    # phone_number = Column(String, nullable=False)
    
    events = relationship("Event", back_populates="organizer")
    
    
class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    image = Column(LargeBinary, nullable=False)
    image_mime = Column(String, nullable=False)
    # image_url = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')) 
    
    user = relationship("User")
    
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, nullable=False)
    organizer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    location = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=True)
    capacity = Column(Integer, nullable=True)  
    image_url = Column(String, nullable=True)       
    image_file = Column(LargeBinary, nullable=True) 
    image_mime = Column(String, nullable=True) 
    visibility = Column(Enum(VisibilityEnum), nullable=False, default=VisibilityEnum.PUBLIC)
    event_link = Column(String, nullable=True)
    invite_token = Column(String, nullable=True)  
    invite_token_expiration = Column(DateTime, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"), onupdate=text("now()"))
    @property
    def invite_url(self):
        return f"https://paytix.com/invite/{self.invite_token}"
    
    
    organizer = relationship("User", back_populates="events")
    tickets = relationship("Ticket", back_populates="event", cascade="all, delete-orphan")
    invites = relationship("EventInvite", back_populates="event", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="event", cascade="all, delete-orphan")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, nullable=False)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, nullable=False)  # e.g., "VIP", "General"
    price = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    currency = Column(String(3), nullable=False, default="NGN")
    quantity_total = Column(Integer, nullable=False)  # total tickets available
    quantity_sold = Column(Integer, nullable=False, default=0)
    per_person_limit = Column(Integer, nullable=True)  # optional purchase cap
    is_seat_based = Column(Boolean, nullable=False, default=False)  # if True, tie to seat map
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    event = relationship("Event", back_populates="tickets")
    orders = relationship("Order", back_populates="ticket", cascade="all, delete-orphan")


class EventInvite(Base):
    __tablename__ = "event_invites"

    id = Column(Integer, primary_key=True, nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # NULL if not registered yet
    token = Column(String, nullable=True)  # unique per-invite link (optional)
    status = Column(Enum(InviteStatusEnum), nullable=False, default=InviteStatusEnum.PENDING)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    event = relationship("Event", back_populates="invites")
    user = relationship("User")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)

    quantity = Column(Integer, nullable=False)
    amount_paid = Column(DECIMAL(10, 2), nullable=False)  # for Paystack reconciliation
    payment_status = Column(String, nullable=False, default="pending")  # could also be an Enum
    paystack_reference = Column(String, nullable=True)  # for payment verification

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    event = relationship("Event", back_populates="orders")
    ticket = relationship("Ticket", back_populates="orders")
    user = relationship("User")