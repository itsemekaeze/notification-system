from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.notification.models import NotificationCreate, NotificationResponse
from src.database.core import get_db
from sqlalchemy.orm import Session
from src.entities.notification import Notification

router = APIRouter(
    tags=["Notification"],
    prefix="/notification"
)

@router.post("/", response_model=NotificationResponse)
async def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db)
):
    """Create a new notification (triggers real-time delivery via PostgreSQL NOTIFY)"""
    db_notification = Notification(**notification.dict())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

@router.get("/{user_id}", response_model=List[NotificationResponse])
def get_notifications(
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    
    notifications = db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    return notifications

@router.patch("/{notification_id}/read")
def mark_as_read(notification_id: int, db: Session = Depends(get_db)):
    """Mark a notification as read"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}

@router.delete("/{notification_id}")
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    """Delete a notification"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(notification)
    db.commit()
    return {"message": "Notification deleted"}