from core.plugins.types.plugin import Plugin
from fastapi import FastAPI
from lib.scrape.navegator import Navigator
from .settings import settings
from asyncio.exceptions import CancelledError
import lib.scrape.base as scrape

class ScraperPlugin(Plugin):

    async def initialize(self, app: FastAPI):
        try:
            print("[ScraperPlugin] Initializing...")
            Navigator(settings.email_linkedin, settings.password_linkedin)
        except Exception as e:
            print(f"[ScraperPlugin] Error initializing: {e}")
            Navigator.terminate_instance()
        
    async def terminate(self, app: FastAPI):
        try:
            print("[ScraperPlugin] Terminating...")
            Navigator.terminate_instance()
        except Exception as e:
            print(f"[ScraperPlugin] Error during termination: {e}")
           
