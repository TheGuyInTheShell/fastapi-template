import time
from typing import Optional, Any
from .base import BaseCacheBackend


class InMemoryCacheBackend(BaseCacheBackend):
    def __init__(self):
        self._cache = {}

    async def get(self, key: str) -> Optional[str]:
        return self._get_sync(key)

    def _get_sync(self, key: str) -> Optional[str]:
        data = self._cache.get(key)
        if not data:
            return None
        value, expire_at = data
        if expire_at and time.time() > expire_at:
            del self._cache[key]
            return None
        return value

    async def set(self, key: str, value: Any, ttl: int = 60) -> None:
        self._set_sync(key, value, ttl)

    def _set_sync(self, key: str, value: Any, ttl: int = 60) -> None:
        expire_at = time.time() + ttl
        self._cache[key] = (value, expire_at)

    async def delete(self, key: str) -> None:
        self._delete_sync(key)

    def _delete_sync(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]

    def sync_get(self, key: str) -> Any:
        return self._get_sync(key)

    def sync_set(self, key: str, value: Any, ttl: int = 60) -> None:
        self._set_sync(key, value, ttl)

    def sync_delete(self, key: str) -> None:
        self._delete_sync(key)
