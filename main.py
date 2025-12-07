from dotenv import load_dotenv

import asyncio

from sockets.main import init_sockets

load_dotenv()


import socketio

from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles

from fastapi.templating import Jinja2Templates


import core.jobs as jobs

import core.middlewares as middlewares
from admin.templates import init_admin

from core.database import BaseAsync, BaseSync, SessionAsync, engineSync, get_async_db

from core.routes import api_router

from core.init_owner import initialize_owner

from modules.permissions.services import create_permissions_api

from prometheus_fastapi_instrumentator import Instrumentator



app = FastAPI()


app = middlewares.initialazer(app)


app = jobs.set_jobs(app)


# Socket io (sio) create a Socket.IO server

socket_app = init_sockets(app)
app.mount("/sio", socket_app)


app.mount("/public", StaticFiles(directory="public"))


# Node modules

app.mount("/node_modules", StaticFiles(directory="node_modules"), name="node_modules")


# Static files

app.mount("/static", StaticFiles(directory="admin/static"), name="admin")


# Jinja2 templates for admin panel

templates = Jinja2Templates(directory="admin/src")

init_admin(templates, app)

app.include_router(api_router)


# Prometheus

Instrumentator().instrument(app).expose(app)


# Database initialization models

BaseSync.metadata.create_all(engineSync)

BaseAsync.metadata.create_all(engineSync)


# Database initialization permissions and owner

asyncio.ensure_future(create_permissions_api(app.routes, SessionAsync))

asyncio.ensure_future(initialize_owner(SessionAsync))



all_declared_classes = BaseAsync.metadata.tables


for class_ in all_declared_classes:
    print(class_)

