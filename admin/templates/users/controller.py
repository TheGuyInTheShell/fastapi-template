from fastapi import Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_async_db
from app.modules.users.models import User
from app.modules.roles.models import Role


class InitTemplate:
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates
        self.router = APIRouter()

    def add_page(self):
        @self.router.get("", response_class=HTMLResponse)
        async def users_page(
            request: Request,
            ord_by: str = "id",
            pag: int = 1,
            ord: str = "desc",
            db: AsyncSession = Depends(get_async_db),
        ):

            # Get all users with roles
            users = await User.find_some(db, status="exists", pag=pag, ord=ord)

            roles_in_users = await Role.find_all(db)

            roles_by_id = {}

            for role in roles_in_users:
                roles_by_id[role.id] = role

            return self.templates.TemplateResponse(
                "pages/users.html",
                context={
                    "request": request,
                    "users": users,
                    "pag": pag,
                    "ord": ord,
                    "ord_by": ord_by,
                    "roles_in_users": roles_in_users,
                    "roles_by_id": roles_by_id,
                },
            )

        @self.router.get("/edit/{id}", response_class=HTMLResponse)
        async def get_edit_page(
            request: Request, id: int, db: AsyncSession = Depends(get_async_db)
        ):
            user = await User.find_one(db, id)
            roles = await Role.find_all(db)

            return self.templates.TemplateResponse(
                "pages/users_edit.html",
                context={
                    "request": request,
                    "user": user,
                    "roles": roles,
                    "success": None,
                },
            )

        @self.router.post("/edit/{id}", response_class=HTMLResponse)
        async def post_edit_page(
            request: Request,
            id: int,
            username: str = Form(...),
            full_name: str = Form(...),
            email: str = Form(...),
            role_id: int = Form(...),
            db: AsyncSession = Depends(get_async_db),
        ):
            try:
                await User.update(
                    db,
                    id,
                    {
                        "username": username,
                        "full_name": full_name,
                        "email": email,
                        "role_ref": role_id,
                    },
                )

                # Fetch updated data to re-render if needed, or just redirect/show success
                user = await User.find_one(db, id)
                roles = await Role.find_all(db)

                return self.templates.TemplateResponse(
                    "pages/users_edit.html",
                    context={
                        "request": request,
                        "user": user,
                        "roles": roles,
                        "success": True,
                    },
                )
            except Exception as e:
                user = await User.find_one(db, id)
                roles = await Role.find_all(db)
                return self.templates.TemplateResponse(
                    "pages/users_edit.html",
                    context={
                        "request": request,
                        "user": user,
                        "roles": roles,
                        "success": False,
                        "detail": str(e),
                    },
                )

    def add_all(self):
        self.add_page()
        return self.router
