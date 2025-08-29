from pydantic import HttpUrl
from .database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, LargeBinary
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')) 
    image = Column(LargeBinary, nullable=False)
    image_mime = Column(String, nullable=False)
    # phone_number = Column(String, nullable=False)
    
    
    
