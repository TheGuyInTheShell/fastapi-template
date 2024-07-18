import os
from importlib import import_module

from fastapi import FastAPI

from fastapi_socketio import SocketManager


def init_sockets_events(sio: SocketManager, app: FastAPI):
    module_names = [f for f in os.listdir('sockets')]
    
    for module_name in module_names:
        try:
            if module_name.find('.py') != -1 or module_name.find('pycache') != -1 : continue
            module = import_module(f"sockets.{module_name}.events")
            print(f"Importing module {module_name}")
            module.socket_services(sio, app, module_name) 
        except ValueError as e:
            print(f"Error importing module {module_name}: {e}")
            continue