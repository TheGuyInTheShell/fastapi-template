from fastapi import Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_async_db
from modules.users.models import User

class InitTemplate:
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates
        self.router = APIRouter()

    def add_page(self):
        @self.router.get("", response_class=HTMLResponse)
        async def users_page(request: Request, db: AsyncSession = Depends(get_async_db)):
            # Get all users with roles
            users = await User.find_all(db, status="exists")
            deleted_users = await User.find_all(db, status="deleted")
            
            return self.templates.TemplateResponse(
                "pages/users.html",
                context={
                    "request": request,
                    "users": users,
                    "deleted_users": deleted_users,
                },
            )

    def add_all(self):
        self.add_page()
        return self.router
