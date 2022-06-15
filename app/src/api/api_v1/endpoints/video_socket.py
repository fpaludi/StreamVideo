import traceback
import cv2
import base64
import asyncio as aio
from cv2 import trace
from fastapi import WebSocket, APIRouter
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse
from fastapi.websockets import WebSocketDisconnect
from starlette.websockets import WebSocketState
from websockets.exceptions import ConnectionClosedError
from logger import get_logger
from services.factories import video_reader
from utils.websockets import check_gracefully_close_connection

router = APIRouter()
logger = get_logger(__name__)


@router.get("/ws")
async def get():
    return FileResponse('static/show_video.html')


@router.websocket("/ws/testchannel")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        logger.info(f"Client start connection {websocket.client.host}")
        while True:
            frame = video_reader.get_frame()
            if not frame is None:
                _, buffer = cv2.imencode('.jpg', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                data = base64.b64encode(buffer).decode("utf-8")
                await websocket.send_text(data)

            # Need to gracefully close client connections
            await check_gracefully_close_connection(websocket)

    except (WebSocketDisconnect, aio.exceptions.IncompleteReadError, ConnectionClosedError):
        logger.info("Client drop connection")
    except Exception as exc:
        logger.warning(f"Close with uncached exception")
        print(traceback.format_exc())
    finally:
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await check_gracefully_close_connection(websocket)
            await websocket.close()

