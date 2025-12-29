from typing import Dict, Set
import json
import asyncpg
from src.database.core import ASYNC_DATABASE_URL
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from src.database.core import get_db
from sqlalchemy.orm import Session
from src.entities.notification import Notification

router = APIRouter()



@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, db: Session = Depends(get_db)):
    """WebSocket connection for real-time notifications"""
    await manager.connect(websocket, user_id)
    
    try:
        # Send existing unread notifications on connect
        unread = db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False).all()
        
        for notif in unread:
            await websocket.send_json({
                "id": notif.id,
                "title": notif.title,
                "message": notif.message,
                "type": notif.type,
                "created_at": notif.created_at.isoformat()
            })
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Handle client messages if needed (e.g., mark as read)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)
        

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        print(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        print(f"User {user_id} disconnected")
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.add(connection)
            
            # Clean up disconnected websockets
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)

manager = ConnectionManager()

class PostgresNotifier:
    def __init__(self):
        self.connection = None
        self.listening = False
    
    async def connect(self):
        self.connection = await asyncpg.connect(ASYNC_DATABASE_URL)
        await self.connection.add_listener('new_notification', self.notification_callback)
        self.listening = True
        print("PostgreSQL LISTEN started")
    
    async def notification_callback(self, conn, pid, channel, payload):
        """Called when a NOTIFY is received from PostgreSQL"""
        try:
            data = json.loads(payload)
            user_id = data.get('user_id')
            notification = data.get('notification')
            
            # Send to connected WebSocket clients
            await manager.send_personal_message(notification, user_id)
        except Exception as e:
            print(f"Error processing notification: {e}")
    
    async def close(self):
        if self.connection:
            await self.connection.close()

postgres_notifier = PostgresNotifier()


