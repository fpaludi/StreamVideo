import traceback
import cv2
import base64
import asyncio as aio
from fastapi import WebSocket, APIRouter
from starlette.responses import FileResponse
from logger import get_logger
from core.video_socket import VideoSocket


router = APIRouter()
logger = get_logger(__name__)


@router.get("/ws")
async def get():
    return FileResponse('static/show_video.html')

@router.websocket("/ws/testchannel")
async def websocket_endpoint(websocket: WebSocket):
    video_socket = VideoSocket(websocket)
    loop = aio.get_running_loop()
    await aio.gather(video_socket.run())
    #loop.run_until_complete(video_socket.run())
