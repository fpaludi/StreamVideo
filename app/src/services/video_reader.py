from typing import Optional
import time
from threading import Thread
import numpy as np
import cv2
from logger import get_logger
from core.fps import FPS
import asyncio as aio
from asyncio import Queue, QueueEmpty, QueueFull


class VideoReader:
    def __init__(self, source, max_size=1, clean_if_full=True) -> None:
        self._source = source
        self._capture = cv2.VideoCapture(self._source)
        self._queue = Queue(maxsize=max_size)
        self._queue_size = max_size
        self._clean_if_full = clean_if_full
        self._running = False
        # self._thread: Optional[Thread] = None
        self._logger = get_logger(__class__.__name__)

    async def _loop(self) -> None:
        while self._running:
            # self._logger.info("Running")
            frame = await self._read_from_source()
            try:
                await aio.wait_for(self._queue.put(frame), 0.1)
            except (QueueFull, aio.TimeoutError):
                self._logger.info("Video reader queue is full.")
                if self._clean_if_full:
                    self._logger.debug("Cleaning video reader queue")
                    self.clean_queue(half=True)

    @FPS("RTSP Reader FPS", 5)
    async def _read_from_source(self) -> Optional[np.ndarray]:
        retval, frame = self._capture.read()
        if not retval:
            frame = await self._reconnect()
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) if retval else None

    @FPS("Consumer FPS", 5)
    async def get_frame(self) -> Optional[np.ndarray]:
        frame = await self._queue.get()
        self._queue.task_done()
        return frame

    async def start(self) -> None:
        self._logger.info("Starting video reader")
        self._running = True
        aio.gather(self._loop())

    async def stop(self) -> None:
        self._logger.info("Closing video reader")
        self._running = False
        self.clean_queue()
        await self._queue.join()
        # self._capture.release()

    def clean_queue(self, half=False) -> None:
        size = int(self._queue_size / 2) if half else self._queue_size
        for _ in range(size):
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except QueueEmpty:
                break

    async def _reconnect(self) -> np.ndarray:
        attempt = 0
        self._capture = cv2.VideoCapture(self._source)
        while True:
            retval, frame = self._capture.read()
            if retval:
                break
            attempt += 1
            self._logger.warning(f"Trying to reconnect. Attempt: {attempt}")
            await aio.sleep(1)
        return frame
