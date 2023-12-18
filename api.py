from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import FileResponse
from starlette.requests import Request

from managers import TimeManager, GameManager

time_manager = TimeManager()
game_manager = GameManager()

app = FastAPI()


@app.get("/")
def get_html(request: Request):
    print(request.url.path)
    return FileResponse("index.html", media_type="text/html")


@app.get("/get_server_timestamp")
def get_server_timestamp():
    server_timestamp = datetime.utcnow()
    return {"timestamp": server_timestamp}


@app.get("/get_timestamp_after_delay")
def get_timestamp_after_delay():
    delay_seconds = 5
    timestamp = time_manager.timestamp_after_delay(delay_seconds)
    return {"timestamp": timestamp}
