from fastapi import APIRouter, Depends
from typing import List
from src.notification.models import NotificationCreate, NotificationResponse
from src.database.core import get_db
from sqlalchemy.orm import Session
from src.notification.service import create_notifications, get_notifications, mark_as_reads, delete_notifications

router = APIRouter(
    tags=["Notification"],
    prefix="/notification"
)

@router.post("/", response_model=NotificationResponse)
async def create_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    return create_notifications(notification, db)

@router.get("/{user_id}", response_model=List[NotificationResponse])
def get_notification(user_id: str, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    
    return get_notifications(user_id, skip, limit, db)

@router.patch("/{notification_id}/read")
def mark_as_read(notification_id: int, db: Session = Depends(get_db)):
   
   return mark_as_reads(notification_id, db)

@router.delete("/{notification_id}")
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    
    return delete_notifications(notification_id, db)