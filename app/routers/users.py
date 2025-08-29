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
async def create_user(email: str = Form(...),
                name: str = Form(...),
                password: str = Form(...),
                confirm_password: str = Form(...),
                image: UploadFile = File(...),
                db: Session = Depends(get_db)):
    
    user_exisits = db.query(models.User).filter(models.User.email == email).first()
    if user_exisits:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"User already exists")
    
    if password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
        
    if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is not an image")

    # Read file bytes (async)
    raw = await image.read()
    await image.close()

    # Use Pillow to open, resize, compress
    try:
        img = Image.open(BytesIO(raw))
    except UnidentifiedImageError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file")

    # Force convert to RGB to avoid issues with PNG alpha when saving as JPEG
    img = img.convert("RGB")


    # Save compressed version to bytes (WebP recommended for better compression),
    # change format to "JPEG" if you prefer.
    out = BytesIO()
    img.save(out, format="WEBP", quality=85)   # quality ~85 = good visual balance
    img_bytes = out.getvalue()
        
    hashed_password = utils.hash(password)
    password = hashed_password
    new_user = models.User( 
        email=email,
        password=hashed_password,
        name=name,
        image=img_bytes,            
        image_mime=image.content_type
        )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return schemas.User(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        created_at=new_user.created_at,
        image=None,
        image_mime=new_user.image_mime,
        image_url=f"/users/{new_user.id}/image"
    )

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
            name=u.name,
            email=u.email,
            created_at=u.created_at,
            image=None,
            image_mime=u.image_mime,
            image_url=f"/users/{u.id}/image" 
        ))
        return result


@router.get("/{user_id}/image")
def get_user_image(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or not user.image:
        return Response(status_code=status.HTTP_404_NOT_FOUND, detail=f"Image not found")
    return Response(content=user.image, media_type=user.image_mime)





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
    return users

    