from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from starlette.requests import Request

from managers import TimeManager, GameManager, WebSocketHandler


app = FastAPI()
time_manager = TimeManager()
game_manager = GameManager()

# =============================================================================
# GET
# =============================================================================

@app.get("/")
def get_html(request: Request):
    print(request.url.path)
    return FileResponse("index.html", media_type="text/html")


@app.get("/get_server_timestamp")
def get_server_timestamp():
    return {"timestamp": time_manager.now()}


@app.get("/get_timestamp_after_delay")
def get_timestamp_after_delay():
    delay_seconds = 5
    timestamp = time_manager.timestamp_after_delay(delay_seconds)
    return {"timestamp": timestamp}


# =============================================================================
# WEB SOCKET
# =============================================================================

@app.websocket("/ws")
async def websocket_handler(websocket: WebSocket):
    websocket_instance = WebSocketHandler()
    await websocket_instance.on_connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            await websocket_instance.on_receive(websocket, data)
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        await websocket_instance.on_disconnect(websocket)