from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from starlette.requests import Request

from managers import WebSocketHandler


app = FastAPI()


# ==== HTTP ====
@app.get("/")
def get_html(request: Request):
    return FileResponse("index.html", media_type="text/html")


# ==== WEBSOCKET ====

class WebSocketError(Exception):
    pass


@app.websocket("/ws")
async def websocket_handler(websocket: WebSocket):
    websocket_instance = WebSocketHandler()
    await websocket_instance.on_connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            await websocket_instance.on_receive(websocket, data)
    except Exception as e:
        raise WebSocketError(e)
    finally:
        await websocket_instance.on_disconnect(websocket)
