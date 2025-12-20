from core.utils.import_modules import import_modules


from fastapi import APIRouter, Depends


from core.event import ChannelEvent


channel = ChannelEvent()


api_router = APIRouter()



@api_router.get("/check", dependencies=[])

async def response():
    # channel.emit_to("test").run("test")

    return {"result": "Ok!"}

routes = import_modules(api_router)


