from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from src.database.core import Base



class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    title = Column(String)
    message = Column(String)
    type = Column(String)  # info, success, warning, error
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)