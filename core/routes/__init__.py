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

api_router.dependencies = [Depends(ROLE_VERIFY, omit_routes=["auth", "auth/sign-in", "auth/sign-up", "auth/refresh-token"]) ]

import_modules(api_router)