import os
from importlib import import_module
from fastapi import APIRouter, Depends
from core.middlewares.role_verify import ROLE_VERIFY
import asyncio
from core.database import SessionAsync
from app.modules.permissions.services import create_permissions_api


def import_modules(router: APIRouter, base_path: str = "app/modules", prefix: str = ""):
    for root, dirs, files in os.walk(base_path):
        if "controller.py" in files:
            # Normalize path to use dots for Python indexing
            normalized_root = root.replace("\\", "/").replace("/", ".")
            normalized_base = base_path.replace("\\", "/").replace("/", ".")
            
            # Extract module name relative to base_path
            if normalized_root.startswith(normalized_base):
                # Remove base_path prefix and leading dot
                module_name = normalized_root[len(normalized_base):].lstrip(".")
                # Use the normalized path for import_module
                module_import_path = normalized_root
            else:
                # Fallback: skip this directory if it doesn't match expected pattern
                print(f"Skipping unexpected path: {root}")
                continue
            try:
                module = import_module(f"{module_import_path}.controller")
                route_prefix = f"{prefix}/{module_name.replace('.', '/')}"
                router.include_router(
                    module.router,
                    prefix=route_prefix,
                    dependencies=(
                        [Depends(ROLE_VERIFY())] if module_name != "auth" else []
                    ),
                )
                print(f"Importing API module: {module_name}")
            except Exception as e:
                print(f"Error importing API module {module_name}: {e}")

    return [{"routes": router.routes.copy(), "type": "API"}]


def import_webhooks(router: APIRouter, base_path: str = "app/webhooks/in", prefix: str = ""):
    for root, dirs, files in os.walk(base_path):
        if "controller.py" in files:
            normalized_root = root.replace("\\", "/").replace("/", ".")
            normalized_base = base_path.replace("\\", "/").replace("/", ".")
            
            if normalized_root.startswith(normalized_base):
                module_name = normalized_root[len(normalized_base):].lstrip(".")
                module_import_path = normalized_root
            else:
                continue
            try:
                module = import_module(f"{module_import_path}.controller")
                route_prefix = f"{prefix}/{module_name.replace('.', '/')}"
                router.include_router(
                    module.router,
                    prefix=route_prefix,
                    dependencies=[], # No authentication for webhooks
                )
                print(f"Importing Webhook module: {module_name}")
            except Exception as e:
                print(f"Error importing Webhook module {module_name}: {e}")

    return [{"routes": router.routes.copy(), "type": "Webhook"}]


def load_subscribers(base_path: str = "app/webhooks/out"):
    for root, dirs, files in os.walk(base_path):
        if "subscriber.py" in files:
            # Use relative path from current working directory to calculate module path
            rel_path = os.path.relpath(root, os.getcwd())
            normalized_root = rel_path.replace("\\", "/").replace("/", ".")
            module_path = f"{normalized_root}.subscriber"
            try:
                import_module(module_path)
                print(f"Loaded webhook subscriber: {module_path}")
            except Exception as e:
                print(f"Error loading webhook subscriber {module_path}: {e}")
