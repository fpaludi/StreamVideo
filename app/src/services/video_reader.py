from typing import Optional
import time
from queue import Queue, Empty, Full
from threading import Thread
import numpy as np
import cv2
from logger import get_logger
from core.fps import FPS

class VideoReader:
    def __init__(self, source, max_size=1, clean_if_full=True) -> None:
        self._source = source
        self._capture = cv2.VideoCapture(self._source)
        self._queue = Queue(maxsize=max_size)
        self._clean_if_full = clean_if_full
        self._running = False
        self._thread: Optional[Thread] = None

        self._logger = get_logger(__name__)

    def _loop(self) -> None:
        while self._running:
            frame = self._read_from_source()
            try:
                self._queue.put(frame, block=False)
            except Full:
                self._logger.debug("Video reader queue is full.")
                if self._clean_if_full:
                    self._logger.debug("Cleaning video reader queue")
                    self.clean_queue()

    @FPS("RTSP Reader FPS", 5)
    def _read_from_source(self) -> Optional[np.ndarray]:
        retval, frame = self._capture.read()
        if not retval:
            frame = self._reconnect()
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) if retval else None

    @FPS("Consumer FPS", 5)
    def get_frame(self) -> Optional[np.ndarray]:
        frame = self._queue.get()
        self._queue.task_done()
        return frame

    def start(self) -> None:
        self._logger.info("Starting video reader")
        self._running = True
        self._thread = Thread(
            target=self._loop, args=(), daemon=True  ## FIXME: Add necessary to make daemon=False
        )
        self._thread.start()

    def stop(self) -> None:
        self._logger.info("Closing video reader")
        self._running = False
        self.clean_queue()
        self._queue.join()
        # self._capture.release()
        if self._thread:
            self._thread.join()

    def clean_queue(self) -> None:
        while not self._queue.empty():
            self._queue.get()
            self._queue.task_done()

    def _reconnect(self) -> np.ndarray:
        attempt = 0
        self._capture = cv2.VideoCapture(self._source)
        while True:
            retval, frame = self._capture.read()
            if retval:
                break
            attempt += 1
            self._logger.warning(f"Trying to reconnect. Attempt: {attempt}")
            time.sleep(1)
        return frame
