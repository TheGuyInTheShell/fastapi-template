import asyncio

from fastapi_socketio import SocketManager


class Streaming():
    sources: list = []
    sio: SocketManager = None
    
    def __init__(self, socket_manager: SocketManager, namespace: str):
        self.sio = socket_manager
        self.namespace = namespace
        
    async def send(self, source_name: str):
        try:
            pass
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(e)