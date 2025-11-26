from typing import Annotated
from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from modules.roles.models import Role
from modules.permissions.models import Permission
from modules.role_permissions.services import get_role_permissions, assign_permission_to_role, remove_permission_from_role


class InitTemplate:
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates
        self.router = APIRouter()

    def add_page(self):
        @self.router.get("", response_class=HTMLResponse)
        async def roles_page(request: Request, db: AsyncSession = Depends(get_async_db)):
            # Get all roles
            roles = await Role.find_some(db, pag=1, ord="asc", status="exists", filters={})
            
            return self.templates.TemplateResponse(
                "pages/roles.html",
                context={
                    "request": request,
                    "roles": roles,
                },
            )

    def add_partials(self):
        
        @self.router.post("/partial/create", response_class=HTMLResponse)
        async def create_role(
            request: Request,
            name: Annotated[str, Form()],
            description: Annotated[str, Form()],
            level: Annotated[int, Form()],
            db: AsyncSession = Depends(get_async_db),
        ):
            try:
                # Create role with empty permissions array
                role = Role(
                    name=name,
                    description=description,
                    level=level,
                    permissions=[],
                    disabled=False
                )
                await role.save(db)
                
                return self.templates.TemplateResponse(
                    "partials/roles/create.html",
                    context={"request": request, "success": True, "role": role},
                )
            except Exception as e:
                print(e)
                return self.templates.TemplateResponse(
                    "partials/roles/create.html",
                    context={"request": request, "success": False, "detail": str(e)},
                )

        @self.router.get("/partial/edit/{role_id}", response_class=HTMLResponse)
        async def get_edit_form(
            request: Request,
            role_id: str,
            db: AsyncSession = Depends(get_async_db),
        ):
            try:
                role = await Role.find_one(db, role_id)
                return self.templates.TemplateResponse(
                    "partials/roles/edit.html",
                    context={"request": request, "role": role},
                )
            except Exception as e:
                print(e)
                raise e

        @self.router.post("/partial/edit/{role_id}", response_class=HTMLResponse)
        async def edit_role(
            request: Request,
            role_id: str,
            name: Annotated[str, Form()],
            description: Annotated[str, Form()],
            level: Annotated[int, Form()],
            db: AsyncSession = Depends(get_async_db),
        ):
            try:
                role = await Role.update(
                    db, role_id, {"name": name, "description": description, "level": level}
                )
                
                return self.templates.TemplateResponse(
                    "partials/roles/edit.html",
                    context={"request": request, "success": True, "role": role},
                )
            except Exception as e:
                print(e)
                return self.templates.TemplateResponse(
                    "partials/roles/edit.html",
                    context={"request": request, "success": False, "detail": str(e)},
                )

        @self.router.delete("/partial/delete/{role_id}", response_class=HTMLResponse)
        async def delete_role(
            request: Request,
            role_id: str,
            db: AsyncSession = Depends(get_async_db),
        ):
            try:
                await Role.delete(db, role_id)
                return self.templates.TemplateResponse(
                    "partials/roles/delete.html",
                    context={"request": request, "success": True},
                )
            except Exception as e:
                print(e)
                return self.templates.TemplateResponse(
                    "partials/roles/delete.html",
                    context={"request": request, "success": False, "detail": str(e)},
                )

        @self.router.get("/partial/permissions/{role_id}", response_class=HTMLResponse)
        async def get_permissions_form(
            request: Request,
            role_id: str,
            db: AsyncSession = Depends(get_async_db),
        ):
            try:
                role = await Role.find_one(db, role_id)
                all_permissions = await Permission.find_some(db, pag=1, ord="asc", status="exists", filters={})
                role_permission_uids = set(role.permissions)
                
                return self.templates.TemplateResponse(
                    "partials/roles/permissions.html",
                    context={
                        "request": request,
                        "role": role,
                        "all_permissions": all_permissions,
                        "role_permission_uids": role_permission_uids,
                    },
                )
            except Exception as e:
                print(e)
                raise e

        @self.router.post("/partial/permissions/{role_id}/toggle", response_class=HTMLResponse)
        async def toggle_permission(
            request: Request,
            role_id: str,
            permission_id: Annotated[str, Form()],
            action: Annotated[str, Form()],  # "assign" or "remove"
            db: AsyncSession = Depends(get_async_db),
        ):
            try:
                if action == "assign":
                    await assign_permission_to_role(db, role_id, permission_id)
                elif action == "remove":
                    await remove_permission_from_role(db, role_id, permission_id)
                
                # Return updated permissions list
                role = await Role.find_one(db, role_id)
                all_permissions = await Permission.find_some(db, pag=1, ord="asc", status="exists", filters={})
                role_permission_uids = set(role.permissions)
                
                return self.templates.TemplateResponse(
                    "partials/roles/permissions.html",
                    context={
                        "request": request,
                        "role": role,
                        "all_permissions": all_permissions,
                        "role_permission_uids": role_permission_uids,
                        "success": True,
                    },
                )
            except Exception as e:
                print(e)
                return self.templates.TemplateResponse(
                    "partials/roles/permissions.html",
                    context={"request": request, "success": False, "detail": str(e)},
                )

    def add_all(self):
        self.add_page()
        self.add_partials()
        return self.router
