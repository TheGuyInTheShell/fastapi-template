import asyncio

from fastapi import FastAPI

from socketio import AsyncServer

from core.event import ChannelEvent

from core.middlewares.jwt_verify_socket import wrap_init_connect

from .services import Streaming




def socket_config(sio: AsyncServer, app: FastAPI, module_name: str):

    namespace = f"/{module_name}"
    channel = ChannelEvent()
    handler = wrap_init_connect(sio)
    streaming = Streaming(sio, namespace)

    try:

        @sio.on("connect", namespace=namespace)
        async def on_connect(sid, environ, auth):
            print(f"Client {sid} connected to {namespace}")
            result = await handler(sid, environ, auth)
            if result:
                await sio.emit(
                    event='connect_info',
                    data={
                        'message': 'Connection successful!',
                        'status': 'ready'
                    },
                    room=sid,
                    namespace=namespace
                )
            return result

        @channel.subscribe_to("test")
        async def test(args):

            print(args)

            await sio.emit("test2", "XDDD", namespace=namespace)

        # asyncio.ensure_future(streaming.send('0'), loop=asyncio.get_event_loop())



    except ValueError as e:
        print(e)


