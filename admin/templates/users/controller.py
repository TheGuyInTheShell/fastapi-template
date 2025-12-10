from fastapi import Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_async_db
from modules.users.models import User
from modules.roles.models import Role

class InitTemplate:
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates
        self.router = APIRouter()

    def add_page(self):
        @self.router.get("", response_class=HTMLResponse)
        async def users_page(request: Request, ord_by: str = "id", pag: int = 1, ord: str = "desc", db: AsyncSession = Depends(get_async_db)):

            # Get all users with roles
            users = await User.find_some(db, status="exists", pag=pag, ord=ord)

            roles_in_users = await Role.find_all(db)


            roles_by_id = {} 
            
            for role in roles_in_users:
                roles_by_id[role.uid] = role

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

    def add_all(self):
        self.add_page()
        return self.router
