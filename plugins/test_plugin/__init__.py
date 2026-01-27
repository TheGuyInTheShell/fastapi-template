from core.plugins.types.plugin import Plugin
from fastapi import FastAPI

class TestPlugin(Plugin):
    async def initialize(self, app: FastAPI):
        print("[TestPlugin] Initializing...")
        # You could add routes here:
        # app.include_router(...)
        
    async def terminate(self, app: FastAPI):
        print("[TestPlugin] Terminating...")
