from typing import Annotated, List
from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from modules.roles.models import Role
from modules.permissions.models import Permission
from core.database import SessionAsync

class InitTemplate:
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates
        self.router = APIRouter()

    def add_page(self):
        @self.router.get("", response_class=HTMLResponse)
        async def roles_page(request: Request, db: AsyncSession = Depends(get_async_db)):
            # Get all roles (filter out deleted ones)
            all_roles = await Role.find_some(db, pag=1, ord="asc", status="all", filters={})
            roles = [r for r in all_roles if not r.is_deleted]
            
            return self.templates.TemplateResponse(
                "pages/roles.html",
                context={
                    "request": request,
                    "roles": roles,
                },
            )

        @self.router.get("/create", response_class=HTMLResponse)
        async def create_role_page(request: Request, db: AsyncSession = Depends(get_async_db)):
            # Get all permissions for multi-select
            all_perms = await Permission.find_all(db, status="exists")
            all_permissions = [p for p in all_perms]
            
            return self.templates.TemplateResponse(
                "pages/roles_create.html",
                context={
                    "request": request,
                    "all_permissions": all_permissions,
                },
            )

        @self.router.post("/create", response_class=HTMLResponse)
        async def create_role(
            request: Request,
            name: Annotated[str, Form()],
            description: Annotated[str, Form()],
            level: Annotated[int, Form()],
            permissions: Annotated[List[str], Form()] = [],
            db: AsyncSession = Depends(get_async_db),
        ):
            try:
                # Create role with selected permissions
                role = Role(
                    name=name,
                    description=description,
                    level=level,
                    permissions=permissions if permissions else [],
                    disabled=False
                )
                await role.save(db)
                
                # Get all permissions for re-rendering form
                all_perms = await Permission.find_all(db, status="exists")
                all_permissions = [p for p in all_perms]
                
                return self.templates.TemplateResponse(
                    "pages/roles_create.html",
                    context={
                        "request": request,
                        "success": True,
                        "all_permissions": all_permissions,
                    },
                )
            except Exception as e:
                print(e)
                all_perms = await Permission.find_all(db, status="exists")
                all_permissions = [p for p in all_perms]
                return self.templates.TemplateResponse(
                    "pages/roles_create.html",
                    context={
                        "request": request,
                        "success": False,
                        "detail": str(e),
                        "all_permissions": all_permissions,
                    },
                )

        @self.router.get("/edit/{role_id}", response_class=HTMLResponse)
        async def edit_role_page(
            request: Request,
            role_id: str,
            db: AsyncSession = Depends(get_async_db),
        ):
            try:
                role = await Role.find_one(db, role_id)
                all_perms = await Permission.find_all(db, status="exists")
                all_permissions = [p for p in all_perms]
                role_permission_uids = set(role.permissions)
                
                return self.templates.TemplateResponse(
                    "pages/roles_edit.html",
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

        @self.router.post("/edit/{role_id}", response_class=HTMLResponse)
        async def edit_role(
            request: Request,
            role_id: str,
            name: Annotated[str, Form()],
            description: Annotated[str, Form()],
            level: Annotated[int, Form()],
            permissions: Annotated[List[str], Form()] = [],
            db: AsyncSession = Depends(get_async_db),
        ):
            try:
                # Update role with new data including permissions
                role = await Role.update(
                    db, 
                    role_id, 
                    {
                        "name": name, 
                        "description": description, 
                        "level": level,
                        "permissions": permissions if permissions else []
                    }
                )
                
                all_perms = await Permission.find_all(db, status="exists")
                all_permissions = [p for p in all_perms]
                role_permission_uids = set(role.permissions)
                
                return self.templates.TemplateResponse(
                    "pages/roles_edit.html",
                    context={
                        "request": request,
                        "success": True,
                        "role": role,
                        "all_permissions": all_permissions,
                        "role_permission_uids": role_permission_uids,
                    },
                )
            except Exception as e:
                print(e)
                role = await Role.find_one(db, role_id)
                all_perms = await Permission.find_all(db, status="exists")
                all_permissions = [p for p in all_perms]
                role_permission_uids = set(role.permissions)
                
                return self.templates.TemplateResponse(
                    "pages/roles_edit.html",
                    context={
                        "request": request,
                        "success": False,
                        "detail": str(e),
                        "role": role,
                        "all_permissions": all_permissions,
                        "role_permission_uids": role_permission_uids,
                    },
                )

    def add_partials(self):
        # Only keep delete partial for HTMX
        @self.router.delete("/partial/delete/{role_id}", response_class=HTMLResponse)
        async def delete_role(
            request: Request,
            role_id: str,
            db: AsyncSession = Depends(get_async_db),
        ):
            try:
                await Role.delete(db, role_id)
                return HTMLResponse(content="", status_code=200)
            except Exception as e:
                print(e)
                return HTMLResponse(
                    content=f'<div class="alert alert-error"><span>Error: {str(e)}</span></div>',
                    status_code=400
                )

    def add_all(self):
        self.add_page()
        self.add_partials()
        return self.router
