from typing import List
from fastapi import Response, UploadFile, status, HTTPException, Depends, APIRouter, File, Form
from sqlalchemy.orm import Session
from app.oauth2 import get_current_user
from .. import models, schemas, utils
from ..database import get_db, SessionLocal
from io import BytesIO
from PIL import Image, UnidentifiedImageError
import base64

    
router = APIRouter(
    prefix = "/users",
    tags=['users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(users: schemas.UserBase, db: Session = Depends(get_db)):
    
    user_exisits = db.query(models.User).filter(models.User.email == users.email).first()
    if user_exisits:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"User already exists")
    
    hashed_password = utils.hash(users.password)
    users.password = hashed_password
    new_user = models.User(**users.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# @router.get("/", response_model=schemas.UserProfile)
# def get_profile(current_user: models.User = Depends(get_current_user)):
#     return current_user


@router.get("/", response_model=List[schemas.User])    
def get_profile(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    
    result = []
    for u in users:
        image_base64 = base64.b64encode(u.image).decode("utf-8") if u.image else None
        result.append(schemas.User(
            id=u.id,
            first_name=u.first_name,
            last_name=u.last_name,
            email=u.email,
            created_at=u.created_at,
        ))
    return result


# @router.get("/{user_id}/image")
# def get_user_image(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.id == user_id).first()
#     if not user or not user.image:
#         return Response(status_code=status.HTTP_404_NOT_FOUND, detail=f"Image not found")
#     return Response(content=user.image, media_type=user.image_mime)





# @router.get("/users/{user_id}/image")
# def get_user_image(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.id == user_id).first()
#     if not user or not user.image:
#         return {"error": "No image found"}
#     return Response(content=user.image, media_type="image/jpeg")


# @router.get('/{id}', response_model=schemas.User)
# def get_user(id: int, db: Session = Depends(get_db)):
#     users = db.query(models.User).filter(models.User.id == id).first()

#     if not users:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
#                             detail=f"User with id: {id} does not exixt"
#                             )
    # return users

    