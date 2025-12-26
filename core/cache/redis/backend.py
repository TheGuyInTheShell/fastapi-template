import redis.asyncio as redis
import redis as redis_sync
from typing import Any
from ..base import BaseCacheBackend


class RedisCacheBackend(BaseCacheBackend):
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        self._async_client = None
        self._sync_client = None
        self._connect()

    def _connect(self):
        # Initialize Sync Client
        self._sync_client = redis_sync.Redis(
            host=self._host, port=self._port, decode_responses=True
        )
        # Check connection
        self._sync_client.ping()

        # Initialize Async Client
        self._async_client = redis.Redis(
            host=self._host, port=self._port, decode_responses=True
        )

    async def get(self, key: str) -> Any:
        return await self._async_client.get(key)

    async def set(self, key: str, value: Any, ttl: int = 60) -> None:
        await self._async_client.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        await self._async_client.delete(key)

    def sync_get(self, key: str) -> Any:
        return self._sync_client.get(key)

    def sync_set(self, key: str, value: Any, ttl: int = 60) -> None:
        self._sync_client.set(key, value, ex=ttl)

    def sync_delete(self, key: str) -> None:
        self._sync_client.delete(key)
