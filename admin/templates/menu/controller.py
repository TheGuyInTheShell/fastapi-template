from fastapi import Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_async_db, SessionAsync
from admin.templates.menu.services import MenuService
from admin.templates.menu.seed import ensure_default_menu
from fastapi import Depends
import asyncio

# Menu Controller
class InitTemplate:

    async def init_menu(self):
        try:
            async with SessionAsync() as session:
                await ensure_default_menu(session)
                await session.close()
        except Exception as e:
            print(f"Error initializing menu: {e}")


    def __init__(self, templates: Jinja2Templates):
        self.templates = templates
        self.router = APIRouter()
        asyncio.ensure_future(self.init_menu())


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

            # Authentication Middleware sets request.state.user
            if not hasattr(request.state, "user"):
                return []
            
            user = request.state.user
            return await service.get_menu(user, session)


    def add_all(self):
        self.add_page()
        self.add_partials()
        self.add_endpoints()
        return self.router
