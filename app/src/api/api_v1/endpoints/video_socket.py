import cv2
import base64
from fastapi import WebSocket, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocketDisconnect
from starlette.websockets import WebSocketState
from logger import get_logger
from services.factories import video_reader

router = APIRouter()
logger = get_logger(__name__)


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Video</title>
    </head>
    <body>
        <h1>WebSocket Video</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>

        <ul id='messages'>
        </ul>

        <div id="count"></div>
        <div id="img"></div>
        <img id="img2"> </img>

        <script>
            var ws = new WebSocket("ws://localhost:8000/ws/testchannel");
            ws.onmessage = function(msg) {
                var image = document.getElementById('img2');
                image.src = 'data:image/jpg;base64,' + msg.data;
                console.log(image.src);
          };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

# image.src = 'data:image/jpg;base64,' + msg.data;

@router.get("/ws")
async def get():
    return HTMLResponse(html)


@router.websocket("/ws/testchannel")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        logger.info(f"Client start connection {websocket.client.host}")
        while True:
            frame = video_reader.get_frame()
            if not frame is None:
                _, buffer = cv2.imencode('.jpg', frame)
                data = base64.b64encode(buffer).decode("utf-8")
                await websocket.send_text(data)
            _ = await websocket.receive_text()  # Need to gracefully close client connections
            #await websocket.send_text(f"you sent message: {data}")
    except WebSocketDisconnect:
        logger.info("Client drop connection")
    finally:
        #if websocket.client_state != WebSocketState.DISCONNECTED:
        #   _ = await websocket.receive_text()  # Need to gracefully close client connections
        #    await websocket.close()
        pass
