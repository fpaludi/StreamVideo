import abc
from typing import Any


class Subscriber(abc.ABC):
    @abc.abstractmethod
    async def notify(self, message: Any):
        pass
