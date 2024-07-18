import asyncio

from fastapi import FastAPI
from fastapi_socketio import SocketManager

from core.event.base import ChannelEvent
from core.middlewares.jwt_verify_socket import wrap_init_connect

from .services import Streaming


def socket_services(sio: SocketManager, app: FastAPI, module_name: str):
    namespace = f"/{module_name}"
    channel = ChannelEvent()
    handler = wrap_init_connect(sio)
    streaming = Streaming(sio, namespace)

    try:

        sio.on("connect", handler=handler, namespace=namespace)

        @channel.subscribe("test")
        async def test(el):
            args, kargs = el
            print(args, kargs)
            sio.emit("test", "XDDD", namespace=namespace)

        # asyncio.ensure_future(streaming.send('0'), loop=asyncio.get_event_loop())

    except ValueError as e:
        print(e)
