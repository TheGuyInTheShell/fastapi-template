import os
from importlib import import_module
import socketio
from fastapi import FastAPI


def init_sockets(app: FastAPI):
    
    module_names = [f for f in os.listdir('sockets')]

    namespaces = []
    
    for module_name in module_names:

        if module_name.find('.py') != -1 or module_name.find('__pycache__') != -1: continue

        namespaces.append(f"/{module_name}")
 

    sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[], path="/sio", namespaces=namespaces, logger=True, engineio_logger=True, allow_upgrades=True)

    for module_name in module_names:

            try:

                if module_name.find('.py') != -1 or module_name.find('__pycache__') != -1: continue

                module = import_module(f"sockets.{module_name}.events")

                print(f"Importing socket module: {module_name}")

                module.socket_config(sio, app, module_name)

            except Exception as e:

                print(f"Error importing module {module_name}: {e}")
                continue

    socketio_app = socketio.ASGIApp(sio, other_asgi_app=app, socketio_path="/sio/")
    
    return socketio_app