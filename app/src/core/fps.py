from typing import Callable
from logger import get_logger
from time import perf_counter


class FPS:
    def __init__(self, legend: str ="FPS", window: float = 5):
        self._legend = legend
        self._window = window
        self._logger = None
        self._counter = 0
        self._last_log_time = perf_counter()

    def __call__(self, func: Callable):
        if not self._logger:
            name = ".".join(func.__qualname__.split(".")[:-1])
            self._logger = get_logger(name)
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)
            self._counter += 1
            t1 = perf_counter()
            time_div = t1 - self._last_log_time
            if time_div > self._window:
                self._logger.info(f"{self._legend}: {self._counter / time_div}")
                self._last_log_time = perf_counter()
                self._counter = 0
            return result
        return inner
