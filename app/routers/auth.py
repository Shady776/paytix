from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from .. import models, schemas, utils, oauth2
from ..database import get_db
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router=APIRouter(
    tags=['Authentication']
)

@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    users = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    
    if not users:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"invalid Credentials")
    
    if not utils.verify(user_credentials.password, users.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=F"Invalid credentials")
    
    access_token = oauth2.create_access_token(data = {"user_id": users.id})
    return{"access_token": access_token, "token_type": "bearer"}
    