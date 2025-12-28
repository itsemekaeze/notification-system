from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
from src.database.core import Base, engine, SessionLocal, ASYNC_DATABASE_URL
from src.websocket.websocket_manager import postgres_notifier
from src.notification.controller import router as notification_router
from src.websocket.websocket_manager import router as websocket_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real-Time Notifications API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup/Shutdown Events
@app.on_event("startup")
async def startup():
    await postgres_notifier.connect()
    
    # Create PostgreSQL trigger function
    async with asyncpg.create_pool(ASYNC_DATABASE_URL) as pool:
        async with pool.acquire() as conn:
            await conn.execute("""
                CREATE OR REPLACE FUNCTION notify_new_notification()
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
            """)
            
            await conn.execute("""
                DROP TRIGGER IF EXISTS new_notification_trigger ON notifications;
                CREATE TRIGGER new_notification_trigger
                AFTER INSERT ON notifications
                FOR EACH ROW
                EXECUTE FUNCTION notify_new_notification();
            """)
    print("Database triggers created")

@app.on_event("shutdown")
async def shutdown():
    await postgres_notifier.close()


@app.get("/")
def root():
    return {"message": "Welcome to Fastapi Notification System"}

app.include_router(notification_router)
app.include_router(websocket_router)