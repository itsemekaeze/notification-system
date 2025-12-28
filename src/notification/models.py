from pydantic import BaseModel
from datetime import datetime


class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str
    type: str = "info"

class NotificationResponse(BaseModel):
    id: int
    user_id: str
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True