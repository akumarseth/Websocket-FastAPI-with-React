from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
import random

# Create application
app = FastAPI(title='FastAPI WebSocket Example')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # can alter with time
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.websocket("/ws/{client_id}")
@app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket, client_id: int):
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    try:
        while True:
            data = await websocket.receive_text()
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            # message = {"time":current_time,"clientId":client_id,"message":data}
            resp = {'value': random.uniform(0, 1)}
            print(resp)
            await manager.broadcast(json.dumps(resp))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # message = {"time":current_time,"clientId":client_id,"message":"Offline"}
        # await manager.broadcast(json.dumps(message))



class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()
