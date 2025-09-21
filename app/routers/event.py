from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import Response, UploadFile, status, HTTPException, Depends, APIRouter, File, Form
from sqlalchemy.orm import Session
from app.oauth2 import get_current_user, get_current_user_optional
from .. import models, schemas, utils
from ..database import get_db, SessionLocal
from io import BytesIO
from PIL import Image, UnidentifiedImageError
import base64
from PIL import Image
import io

    
router = APIRouter(
    prefix = "/events",
    tags=['events']
)

# event: schemas.EventCreate,
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.EventOut)
def create_event(event: schemas.EventCreate,
                #  title: str,
                #   description: str,
                #   category: str,
                #   start_time: str,
                #   capacity: int,
                #   visibility: str,
                #   image_url: Optional[str] = None,
                #   image_file: Optional[UploadFile] = None,
                  db: Session = Depends(get_db), 
                  current_user: int = Depends(get_current_user)):
        event_creation = db.query(models.Event).filter(models.Event.location == event.location).order_by(models.Event.end_time.desc()).first()
                                                    #    models.Event.end_time > datetime.now() ).first()
   
        # if event_creation:
        #         raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, 
        #                             detail=f"Location '{event.location}' is in use until {event.end_time}")
        # next_available_day = event.end_time.date() + timedelta(days=1)
        # if event.start_time.date() < next_available_day:
        #         raise HTTPException(
        #         status_code=400,
        #         detail=f"Location '{event.location}' will only be available from {next_available_day}"
        #     )
           
    
    
        image_bytes = None
        if event.image_file:  
            img = Image.open(event.image_file.file)
            img = img.convert("RGB")
            img_bytes_io = io.BytesIO()
            img.save(img_bytes_io, format="JPEG", optimize=True, quality=60)  
            image_bytes = img_bytes_io.getvalue()
            
            
        event_token = None
        if event.visibility.lower() == "public":
            event_token = utils.generate_event_token()
            expiration = datetime.utcnow() + timedelta(days=1)
            
        invite_token = None
        if event.visibility.lower() == "private":
            invite_token = utils.generate_invite_token()
            expiration = datetime.utcnow() + timedelta(days=1)
            
        invite_link = None
        if invite_token:
            invite_link = f"https://paytix.com/invite/{invite_token}"
            
        event_link = None
        if event_token:
             event_link = f"https://paytix.com/invite/{event_token}"

        new_event_data = event.dict(exclude={"image_file"}) 
        new_event = models.Event(
            organizer_id=current_user.id,
            image_file=image_bytes,
            invite_token=invite_link,
            event_link=event_link,
            invite_token_expiration=expiration,
            **new_event_data
                )
            #     title=title,
            #     description=description,
            #     category=category,
            #     start_time=start_time,
            #     capacity=capacity,
            #     visibility=visibility,
            #     image_url=image_url,
            #     image=image_bytes,
            #     user_id=current_user.id
            # )
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        
        
        # invite_link = None
        # if invite_token:
        #     invite_link = f"https://paytix.com/invite/{invite_token}"
            
        # event_link = None
        # if event_token:
        #      event_link = f"https://paytix.com/invite/{event_token}"
        
        event_out = schemas.EventOut.from_orm(new_event)
        event_out.invite_token = invite_link
        event_out.event_link = event_link
        return event_out
    
@router.get("/", response_model=List[schemas.EventOut])
def get_all_events(db: Session = Depends(get_db)):
    events = db.query(models.Event).all()
    return events

    
@router.get("/my-events", response_model=List[schemas.EventOut])
def get_all_events(db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    events = db.query(models.Event).filter(models.Event.organizer_id == current_user.id).all()
    return events


@router.put("/{id}", response_model=schemas.EventOut)
async def update_event(id: int, update_event: schemas.EventUpdate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    
    event_update = db.query(models.Event).filter(models.Event.id == id)
    event = event_update.first()
    if event == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Event with id: {id} does not exist")
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    image_bytes = None
    if update_event.image_file:  
            img = Image.open(update_event.image_file.file)
            img = img.convert("RGB")
            img_bytes_io = io.BytesIO()
            img.save(img_bytes_io, format="JPEG", optimize=True, quality=60)  
            image_bytes = img_bytes_io.getvalue()
            
            
    invite_token = None
    if event.visibility.lower() == "private":
            invite_token = utils.generate_invite_token()
            expiration = datetime.utcnow() + timedelta(days=1)

    update_data = update_event.dict(exclude={"image_file"}, exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)

 
    if update_event.image_file:
        image_bytes = await update_event.image_file.read() 
        event.image_file = image_bytes
    
    invite_link = None
    if invite_token:
            invite_link = f"https://paytix.com/invite/{invite_token}"
        
    if invite_token:
        event.invite_token = invite_link
    
    updated_event_out = schemas.EventOut.from_orm(event)
    updated_event_out.invite_token = invite_link
    db.commit()
    db.refresh(event)
    return updated_event_out
    

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    event = db.query(models.Event).filter(models.Event.id == id)
    del_event = event.first()
    
    if del_event == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Event with id: {id} does not exist")
        
    if del_event.organizer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")
        
    event_deletion = event.delete(synchronize_session=False)
    db.commit()
    return event_deletion


@router.get("/invite/{invite_token}", response_model=schemas.EventBase)
def get_event_by_invite(
    invite_token: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)  # <-- allows None if not logged in
):
    event = db.query(models.Event).filter(models.Event.invite_token == invite_token).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired invite token"
        )
    
    if current_user:
        return event  
    else:
        # Optionally return limited info
        # You can use another schema like EventPreview
        return event



@router.post("/{event_id}/regenerate_invite_token", response_model=schemas.EventInviteToken)
def regenerate_invite_token(event_id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.organizer_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found or not owned by you")
    
    token = utils.generate_invite_token()
    invite_link = f"https://paytix.com/invite/{token}"
    expiration = datetime.utcnow() + timedelta(days=1)
    
    event.invite_token = token
    event.invite_token_expiration = expiration
    
    db.commit()
    db.refresh(event)
    return event
    


# @router.get("/invite/{token}")
# def view_invite(
#     token: str,
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user_optional)  # <- notice here
# ):
#     invite = db.query(models.EventInvite).filter(models.EventInvite.token == token).first()
#     if not invite:
#         raise HTTPException(status_code=404, detail="Invalid or expired token")
    
#     if current_user:
#         # Logged in user → let them view ticket, buy, etc.
#         return {"message": "Welcome back!", "invite": invite}
#     else:
#         # Not logged in → ask them to register/login first
#         return {"message": "Please create an account or log in to continue", "invite": invite}
