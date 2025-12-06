from core.utils.import_modules import import_modules

from fastapi import APIRouter, Depends

from core.event.base import ChannelEvent

channel = ChannelEvent()

api_router = APIRouter()


@api_router.get("/check", dependencies=[])
def response():
    channel.emit("test", "args")
    return {"result": "Ok!"}

import_modules(api_router)