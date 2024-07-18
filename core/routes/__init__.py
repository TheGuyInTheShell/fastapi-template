import os
from importlib import import_module

from fastapi import APIRouter, Depends

from core.event.base import ChannelEvent
from core.middlewares.role_verify import ROLE_VERIFY

channel = ChannelEvent()

api_router = APIRouter()


@api_router.get("/check", dependencies=[])
def response():
    channel.emit("test", "args")
    return {"result": "Ok!"}


module_names = [f for f in os.listdir("modules")]

for module_name in module_names:
    try:
        module = import_module(f"modules.{module_name}.controller")
        api_router.include_router(module.router, prefix=f"/api/{module_name}")
    except Exception as e:
        print(f"Error importing module {module_name}: {e}")
        continue
