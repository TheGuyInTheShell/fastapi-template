from dotenv import load_dotenv

from sockets.main import init_sockets_events

load_dotenv()
import asyncio

import socketio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import core.jobs as jobs
import core.middlewares as middlewares
from admin.templates import init_templates
from core.database.async_connection import SessionAsync
from core.database.base import BaseAsync, BaseSync
from core.database.sync_connection import engineSync
from core.routes import api_router
from modules.permissions.services import create_permissions_api

app = FastAPI()

app = middlewares.initialazer(app)

app = jobs.set_jobs(app)

# Socket io (sio) create a Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins=[], async_mode="asgi")

socket_app = socketio.ASGIApp(sio)

app.mount(f"/sio/", socket_app)

init_sockets_events(sio=sio, app=app)

app.mount("/public", StaticFiles(directory="public"))

# Monta el directorio de archivos estáticos
app.mount("/static", StaticFiles(directory="admin/static"), name="admin")

# Configura Jinja2 para usar el directorio de plantillas
templates = Jinja2Templates(directory="admin/src")

init_templates(templates, app)

app.include_router(api_router)

BaseSync.metadata.create_all(engineSync)
BaseAsync.metadata.create_all(engineSync)

asyncio.ensure_future(create_permissions_api(app.routes, SessionAsync))


all_declared_classes = BaseAsync.metadata.tables

for class_ in all_declared_classes:
    print(class_)
