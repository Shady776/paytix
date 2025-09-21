from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import Response, UploadFile, status, HTTPException, Depends, APIRouter, File, Form
from sqlalchemy.orm import Session
from app.oauth2 import get_current_user, get_current_user_optional
from .. import models, schemas, utils
from ..database import get_db, SessionLocal

    
router = APIRouter(
    prefix = "/order",
    tags=['order']
)

# event: schemas.EventCreate,
# @router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.EventOut)
# def order_ticket(db: Session = Depends(get_db)):
    
