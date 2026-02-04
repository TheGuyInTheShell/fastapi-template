"""
CLI module generator for creating FastAPI socket structures.
"""
import os
from pathlib import Path


def create_events_template(name: str) -> str:
    """Generate events.py template for sockets"""
    return f'''from fastapi import FastAPI
from socketio import AsyncServer
from core.event import ChannelEvent
from core.middlewares.jwt_verify_socket import wrap_init_connect

# from .services import {name.capitalize()}Service


def socket_config(sio: AsyncServer, app: FastAPI, module_name: str):
    namespace = f"/{{module_name}}"
    channel = ChannelEvent()
    handler = wrap_init_connect(sio)
    # service = {name.capitalize()}Service(sio, namespace)

    try:
        @sio.on("connect", namespace=namespace)
        async def on_connect(sid, environ, auth):
            result = await handler(sid, environ, auth)
            if result:
                await sio.emit(
                    event="connect_info",
                    data={{"message": "Connection successful!", "status": "ready"}},
                    room=sid,
                    namespace=namespace,
                )
            return result

        @sio.on("message", namespace=namespace)
        async def on_message(sid, data):
            print(f"[SOCKET {{module_name}}] Received message: {{data}}")
            await sio.emit("response", {{"message": "Received"}}, room=sid, namespace=namespace)

        @channel.subscribe_to("{name}_event")
        async def on_channel_event(args):
            print(f"[SOCKET {{module_name}}] Channel event received: {{args}}")
            await sio.emit("{name}_update", args, namespace=namespace)

    except Exception as e:
        print(f"[SOCKET {{module_name}}] Error: {{e}}")
'''


def create_services_template(name: str) -> str:
    """Generate services.py template for sockets"""
    return f'''from socketio import AsyncServer


class {name.capitalize()}Service:
    def __init__(self, sio: AsyncServer, namespace: str):
        self.sio = sio
        self.namespace = namespace

    async def broadcast(self, event: str, data: dict):
        """Broadcast data to all connected clients in the namespace"""
        await self.sio.emit(event, data, namespace=self.namespace)

    async def send_to(self, sid: str, event: str, data: dict):
        """Send data to a specific client"""
        await self.sio.emit(event, data, room=sid, namespace=self.namespace)
'''


def generate_socket(name: str):
    """
    Generate a complete socket structure with events and services.
    """
    # Get the project root
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    base_path = project_root / "app" / "sockets" / name

    # Create directory structure
    base_path.mkdir(parents=True, exist_ok=True)
    print(f"[+] Created directory: {base_path}")

    # Create files
    files = {
        '__init__.py': "# Socket module initialization\n",
        'events.py': create_events_template(name),
        'services.py': create_services_template(name),
    }

    for filename, content in files.items():
        file_path = base_path / filename
        if file_path.exists():
            print(f"[SKIP] Already exists: {file_path.relative_to(project_root)}")
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Created: {file_path.relative_to(project_root)}")

    print(f"\n[SUCCESS] Socket '{name}' generated successfully!")
    print(f"[INFO] Location: {base_path}")
    print(f"\n[HINT] Next steps:")
    print(f"   1. Review app/sockets/{name}/events.py")
    print(f"   2. The socket will be automatically loaded by app/sockets/__init__.py")
