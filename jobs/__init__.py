from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

def set_jobs(app: FastAPI) -> FastAPI:
    @app.on_event("startup")
    async def startup_event():
        scheduler.start()

    @app.on_event("shutdown")
    async def shutdown_event():
        scheduler.shutdown()
    
    return app


    