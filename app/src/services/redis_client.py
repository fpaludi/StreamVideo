import abc
import asyncio
from typing import List, Any
import async_timeout
import aioredis
from services.interfaces import Subscriber
from logger import get_logger


class RedisClientBase:
    async def __init__(
        self,
        redis_url: str,
        channel: str,
    ):
        self._channel = channel
        self._redis = aioredis.from_url(redis_url)
        self._pubsub = self._redis.pubsub()
        self._logger = get_logger(self.__class__.__name__)

    @classmethod
    async def build_client(cls, redis_url, channel):
        return cls(redis_url, channel)


class RedisPublisher(RedisClientBase):
    def __init__(self, redis_url, channel):
        super().__init__(redis_url, channel)

    async def publish(self, message: str):
        n_sus = await self._redis.publish(self._channel, message)
        self._logger.debug(f"Message delivered to {n_sus}")


class RedisReaderBase(RedisClientBase, abc.ABC):
    def __init__(self, redis_url, channel):
        super().__init__(redis_url, channel)
        self._running = True

    async def _post_init(self):
        await self._pubsub.subscribe(self._channel)

    async def read(self):
        while self._running:
            try:
                async with async_timeout.timeout(1):
                    message = await self._pubsub.get_message(ignore_subscribe_messages=True)
                    if message is not None:
                        await self._do_task(message["data"].decode())
                    await asyncio.sleep(0.01)
            except asyncio.TimeoutError:
                self._logger.debug(f"No message in {self._channel}")

    def stop(self):
        self._running = False

    @abc.abstractmethod
    async def _do_task(self, message: str):
        pass

    @classmethod
    async def build_client(cls, redis_url, channel):
        client = cls(redis_url, channel)
        await client._post_init()
        return client


class RedisReaderPublisher(RedisReaderBase):
    def __init__(self, redis_url, channel):
        super().__init__(redis_url, channel)
        self._subscribers: List[Subscriber] = []

    def add_subscribers(self, *subscribers: Subscriber):
        self._subscribers.extend(subscribers)

    def remove_subscribers(self, subscriber: Subscriber):
        self._subscribers.remove(subscriber)

    async def _do_task(self, message: str):
        for subscriber in self._subscribers:
            await subscriber.notify(message)


class RedisReaderQueue(RedisReaderBase):
    def __init__(self, redis_url, channel):
        super().__init__(redis_url, channel)
        self._queue = asyncio.Queue(10)

    async def _do_task(self, message: str):
        await self._queue.put(message)

    async def get_message(self) -> str:
        message = await self._queue.get()
        self._queue.task_done()
        return message
