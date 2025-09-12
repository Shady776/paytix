from fastapi import Response, UploadFile, status, HTTPException, Depends, APIRouter, File
from sqlalchemy.orm import Session
from app.oauth2 import get_current_user
from .. import models, schemas
from ..database import get_db
from io import BytesIO
from PIL import Image as PILImage, UnidentifiedImageError

router = APIRouter(
    prefix="/verification",
    tags=['Image Verification']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ImageOut)
async def create_user_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not an image"
        )

    raw = await file.read()

    try:
        img = PILImage.open(BytesIO(raw))
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file"
        )

    img = img.convert("RGB")
    out = BytesIO()
    img.save(out, format="WEBP", quality=100)
    img_bytes = out.getvalue()

    new_image = models.Image(
        user_id=current_user.id,
        image=img_bytes,
        image_mime=file.content_type
    )

    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    image_out = schemas.ImageOut.model_validate(new_image)
    image_out.image_url = f"/verification/{new_image.id}/image"

    return image_out
    # image_url = f"/verification/{new_image.id}/image"

    # return schemas.ImageOut(
    #     id=new_image.id,
    #     user_id=new_image.user_id,
    #     created_at=new_image.created_at,
    #     image_url=image_url
    # )


@router.get("/{image_id}/image")
def get_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    image_record = db.query(models.Image).filter(models.Image.id == image_id).first()
    if not image_record:
        raise HTTPException(status_code=404, detail="Image not found")
    return Response(content=image_record.image, media_type=image_record.image_mime)


# @router.get("/", response_model=schemas.UserProfile)
# def get_profile(current_user: models.User = Depends(get_current_user)):
#     return current_user


# @router.get("/", response_model=List[schemas.User])    
# def get_profile(db: Session = Depends(get_db)):
#     users = db.query(models.User).all()
    
#     result = []
#     for u in users:
#         image_base64 = base64.b64encode(u.image).decode("utf-8") if u.image else None
#         result.append(schemas.User(
#             id=u.id,
#             name=u.name,
#             email=u.email,
#             created_at=u.created_at,
#             image=None,
#             image_mime=u.image_mime,
#             image_url=f"/users/{u.id}/image" 
#         ))
#     return result


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
    return users

    