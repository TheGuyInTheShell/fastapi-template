from core.utils.import_modules import import_modules

from fastapi import APIRouter, Depends

from core.event.base import ChannelEvent
from core.middlewares.role_verify import ROLE_VERIFY

channel = ChannelEvent()

api_router = APIRouter()


@api_router.get("/check", dependencies=[])
def response():
    channel.emit("test", "args")
    return {"result": "Ok!"}

import_modules(api_router)