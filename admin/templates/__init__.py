import os

from importlib import import_module


from fastapi import Depends, FastAPI

from fastapi.responses import FileResponse

from fastapi.templating import Jinja2Templates

from fastapi.routing import APIRouter

from core.middlewares.role_verify_cookie import ROLE_VERIFY_COOKIE

from modules.permissions.services import create_permissions_api

from modules.permissions.const import admin_type

from core.database import SessionAsync

import asyncio
import os
import dotenv

dotenv.load_dotenv()
mode = os.getenv("MODE")
from typing import List, Dict, Any


def init_admin(templates: Jinja2Templates, app: FastAPI) -> List[Dict[str, Any]]:

    @app.get("/favicon.ico")
    async def favicon():

        return FileResponse("admin/static/favicon.ico")

    module_names = [f for f in os.listdir("admin/templates")]
    routes = []

    for module_name in module_names:

        try:

            if module_name.find(".py") != -1 or module_name.find("pycache") != -1:
                continue

            module = import_module(f"admin.templates.{module_name}.controller")

            print(f"Importing ADMIN module {module_name}")

            router: APIRouter = module.InitTemplate(templates).add_all()

            # Apply dependencies when including the router, not after
            # if mode develoment not apply role verify cookie

            dependencies = (
                [Depends(ROLE_VERIFY_COOKIE)] if module_name != "sign-in" else []
            )

            if mode == "DEVELOPMENT":
                dependencies = []

            app.include_router(
                router,
                prefix=f"/admin/{module_name}",
                tags=[f"view - {module_name}"],
                dependencies=dependencies,
            )

        except ValueError as e:

            print(f"Error importing module {module_name}: {e}")
            continue

    return [{"routes": app.routes.copy(), "type": "ADMIN"}]
