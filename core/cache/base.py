from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseCacheBackend(ABC):

    @abstractmethod
    async def get(self, key: str) -> Any:
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 60) -> None:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass

    @abstractmethod
    def sync_get(self, key: str) -> Any:
        pass

    @abstractmethod
    def sync_set(self, key: str, value: Any, ttl: int = 60) -> None:
        pass

    @abstractmethod
    def sync_delete(self, key: str) -> None:
        pass
