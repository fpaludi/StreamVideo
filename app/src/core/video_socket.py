import asyncio as aio
import traceback
import base64
import cv2
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from starlette.websockets import WebSocketState
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from logger import get_logger
from services.factories import video_reader


class VideoSocket:

    def __init__(self, websocket: WebSocket):
        self._websocket = websocket
        self._logger = get_logger(self.__class__.__name__)

    async def run(self):
        await self._websocket.accept()
        try:
            self._logger.info(f"Client start connection {self._websocket.client.host}")
            while True:
                self._logger.debug("Write WEBSOCKET start")
                frame = await video_reader.get_frame()
                if not frame is None:
                    _, buffer = cv2.imencode('.jpg', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                    data = base64.b64encode(buffer).decode("utf-8")
                    await self._websocket.send_text(data)
                    self._logger.debug("Write WEBSOCKET end")
                # Need to gracefully close client connections
                await self._check_gracefully_close_connection()
                # await aio.sleep(1 / 30)
        except (
            WebSocketDisconnect,
            aio.exceptions.IncompleteReadError,
            ConnectionClosedError,
            ConnectionClosedOK
        ):
            self._logger.info("Client drop connection")
        except Exception as exc:
            self._logger.warning(f"Close with uncached exception")
            print(traceback.format_exc())
        finally:
            if self._websocket.client_state != WebSocketState.DISCONNECTED:
                await self._check_gracefully_close_connection()
                await self._websocket.close()

    async def _check_gracefully_close_connection(self):
        try:
            _ = await aio.wait_for(self._websocket.receive_text(), 1e-5)
        except aio.TimeoutError:
            pass
