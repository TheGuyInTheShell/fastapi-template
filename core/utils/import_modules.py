import os
from importlib import import_module
from fastapi import APIRouter, Depends
from core.middlewares.role_verify import ROLE_VERIFY
import asyncio
from core.database import SessionAsync
from modules.permissions.services import create_permissions_api

def import_modules(router: APIRouter, base_path: str = "modules", prefix: str = ""):
    for root, dirs, files in os.walk(base_path):
        if "controller.py" in files:
            module_path = root.replace(os.sep, ".")
            module_name = module_path.split(".", 1)[1]  # Remove the base_path part
            try:
                module = import_module(f"{module_path}.controller")
                route_prefix = f"{prefix}/{module_name.replace('.', '/')}"
                router.include_router(module.router, 
                prefix=route_prefix, 
                dependencies=[ Depends(ROLE_VERIFY()) ] if module_name != "auth" else [] 
                )
                print(f"Importing API module: {module_name}")
            except Exception as e:
                print(f"Error importing API module {module_name}: {e}")

    return [{
        "routes": router.routes.copy(),
        "type": "API"
    }]