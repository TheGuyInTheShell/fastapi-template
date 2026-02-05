from fastapi import Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_async_db
from admin.templates.menu.services import MenuService
from admin.templates.menu.seed import ensure_default_menu

from contextlib import asynccontextmanager

# Menu Controller
class InitTemplate:
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates
        
        @asynccontextmanager
        async def lifespan(app: APIRouter):
            # Startup logic
            async for session in get_async_db():
                await ensure_default_menu(session)
                break
            yield
            # Shutdown logic (if any)
        
        self.router = APIRouter(lifespan=lifespan)

    def add_page(self):

        @self.router.get("")
        async def main_menu(request: Request):
            return {}

    def add_partials(self):

        @self.router.get("/", response_class=HTMLResponse)
        async def admin_read_menu(request: Request):
            return {}
        
        

    def add_endpoints(self):
        @self.router.get("/list")
        async def get_menu_items(request: Request, session: AsyncSession = Depends(get_async_db)):
            service = MenuService()
            # Ensure request.user exists and has role loaded. 
            # Middleware should handle loading user and role.
            # If request.user is not set, this will fail. 
            # Assuming auth middleware is active for /admin routes.
            if not hasattr(request, "user"):
                return []
            return await service.get_menu(request.user, session)


    def add_all(self):
        self.add_page()
        self.add_partials()
        self.add_endpoints()
        return self.router
