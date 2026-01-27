from abc import ABC, abstractmethod
from fastapi import FastAPI

class Plugin(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def initialize(self, app: FastAPI):
        pass

    @abstractmethod
    async def terminate(self, app: FastAPI):
        pass