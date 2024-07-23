from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import redis.asyncio as redis
import asyncio
import os

# Create application
app = FastAPI(title='FastAPI WebSocket Example')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Can alter with time
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                disconnected_connections.append(connection)
        for connection in disconnected_connections:
            self.disconnect(connection)

manager = ConnectionManager()
subscribing_task = None

async def subscribe_to_redis():
    redis_host = os.environ.get("REDIS_HOST", "10.11.153.189")
    redis_port = int(os.environ.get("REDIS_PORT", 6379))
    channel_name = 'channel_test'

    while True:
        try:
            redis_client = redis.Redis(host=redis_host, port=redis_port)
            pubsub = redis_client.pubsub()
            await pubsub.subscribe(channel_name)

            print(f"Subscribed to Redis channel '{channel_name}'")

            async for message in pubsub.listen():
                if message['type'] == 'message':
                    data = message['data'].decode('utf-8')
                    print(f"Received message: {data}")
                    await manager.broadcast(data)
        except Exception as e:
            print(f"Error in Redis subscription: {e}")
        finally:
            if 'pubsub' in locals():
                try:
                    await pubsub.unsubscribe(channel_name)
                    await pubsub.close()
                except Exception as close_error:
                    print(f"Error closing Redis pubsub connection: {close_error}")
            if 'redis_client' in locals():
                try:
                    await redis_client.close()
                except Exception as redis_close_error:
                    print(f"Error closing Redis client: {redis_close_error}")
            await asyncio.sleep(5)  # Delay before attempting to reconnect

@app.on_event("startup")
async def startup_event():
    print("Server started at", datetime.now())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/start-subscription")
async def start_subscription():
    global subscribing_task
    if subscribing_task is not None and not subscribing_task.done():
        raise HTTPException(status_code=400, detail="Subscription already running")

    subscribing_task = asyncio.create_task(subscribe_to_redis())
    return {"message": "Subscription started"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
