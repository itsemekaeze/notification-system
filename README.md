# Real-Time Notifications API

A FastAPI-based real-time notification system using WebSockets and PostgreSQL's LISTEN/NOTIFY mechanism for instant message delivery.

## Features

- **Real-time WebSocket connections** for instant notification delivery
- **PostgreSQL LISTEN/NOTIFY** for efficient database-driven notifications
- **RESTful API** for notification management
- **Automatic triggers** that push notifications when new records are inserted
- **Multi-client support** - users can connect from multiple devices simultaneously
- **Unread notification sync** on connection
- **CORS enabled** for cross-origin requests

## Tech Stack

- **FastAPI** - Modern Python web framework
- **WebSockets** - Real-time bidirectional communication
- **PostgreSQL** - Database with LISTEN/NOTIFY support
- **SQLAlchemy** - SQL toolkit and ORM
- **asyncpg** - Async PostgreSQL driver
- **Pydantic** - Data validation

## Project Structure

```
src/
├── database/
│   └── core.py                 # Database configuration
├── entities/
│   └── notification.py         # Notification model
├── notification/
│   ├── controller.py           # REST API endpoints
│   └── models.py               # Pydantic schemas
└── websocket/
    └── websocket_manager.py    # WebSocket & LISTEN/NOTIFY logic
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd notification-system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install fastapi uvicorn sqlalchemy asyncpg
```

4. Configure your database connection in `src/database/core.py`:
```python
ASYNC_DATABASE_URL = "postgresql://user:password@localhost/dbname"
```

5. Run the application:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### REST API

#### Create Notification
```http
POST /notification/
Content-Type: application/json

{
  "user_id": "user123",
  "title": "New Message",
  "message": "You have a new message",
  "type": "info"
}
```

**Notification Types:** `info`, `success`, `warning`, `error`

#### Get User Notifications
```http
GET /notification/{user_id}?skip=0&limit=50
```

#### Mark as Read
```http
PATCH /notification/{notification_id}/read
```

#### Delete Notification
```http
DELETE /notification/{notification_id}
```

### WebSocket Connection

Connect to receive real-time notifications:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/user123');

ws.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  console.log('New notification:', notification);
};

ws.onopen = () => {
  console.log('Connected to notification service');
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

## How It Works

1. **Client Connection**: User connects via WebSocket at `/ws/{user_id}`
2. **Initial Sync**: All unread notifications are sent immediately upon connection
3. **Real-time Updates**: When a notification is created:
   - It's inserted into the PostgreSQL database
   - A database trigger fires and calls `pg_notify()`
   - The backend listener receives the notification
   - The notification is pushed to all connected WebSocket clients for that user
4. **Multi-device Support**: Users can connect from multiple devices and receive notifications on all of them

## Database Schema

```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    message VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## PostgreSQL Trigger

The system automatically creates a trigger that notifies the application when new notifications are inserted:

```sql
CREATE FUNCTION notify_new_notification()
RETURNS TRIGGER AS $$
DECLARE
    notification_json JSON;
BEGIN
    notification_json = row_to_json(NEW);
    PERFORM pg_notify(
        'new_notification',
        json_build_object(
            'user_id', NEW.user_id,
            'notification', notification_json
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

## Example Usage

### Python Client
```python
import requests
import websocket
import json

# Create a notification
response = requests.post('http://localhost:8000/notification/', json={
    'user_id': 'user123',
    'title': 'Welcome!',
    'message': 'Welcome to our platform',
    'type': 'success'
})

# Connect to WebSocket
def on_message(ws, message):
    data = json.loads(message)
    print(f"Received: {data['title']} - {data['message']}")

ws = websocket.WebSocketApp(
    'ws://localhost:8000/ws/user123',
    on_message=on_message
)
ws.run_forever()
```

### JavaScript/React Client
```javascript
import { useEffect, useState } from 'react';

function NotificationComponent({ userId }) {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${userId}`);
    
    ws.onmessage = (event) => {
      const notification = JSON.parse(event.data);
      setNotifications(prev => [notification, ...prev]);
      
      // Show toast or notification UI
      showNotification(notification);
    };

    return () => ws.close();
  }, [userId]);

  return (
    <div>
      {notifications.map(notif => (
        <div key={notif.id} className={`notification ${notif.type}`}>
          <h4>{notif.title}</h4>
          <p>{notif.message}</p>
        </div>
      ))}
    </div>
  );
}
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

Create a `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost/dbname
ASYNC_DATABASE_URL=postgresql://user:password@localhost/dbname
```

## Production Considerations

- Use environment variables for database credentials
- Implement authentication/authorization for WebSocket connections
- Add rate limiting to prevent abuse
- Use Redis for horizontal scaling across multiple server instances
- Implement reconnection logic in clients
- Add monitoring and logging
- Use a process manager like Supervisor or Docker

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Support

For issues or questions, please open an issue on GitHub.