from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates
from core.database import get_async_db
from fastapi import Depends
from modules.roles.models import Role
from core.database import SessionAsync

class InitTemplate:
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates
        self.router = APIRouter()

    def add_page(self):

        @self.router.get("", response_class=HTMLResponse)
        async def main_api_tokens(request: Request, db: SessionAsync = Depends(get_async_db)):
            roles: List[Role] = await Role.find_all(db)
            return self.templates.TemplateResponse(
                "pages/api-tokens.html",
                context={
                    "request": request,
                    "roles": roles,
                },
            )

    def add_partials(self):

        @self.router.get("/partial/info", response_class=HTMLResponse)
        async def read_info(request: Request):
            return self.templates.TemplateResponse(
                f"partials/info.html",
                context={
                    "request": request,
                },
            )

    def add_all(self):
        self.add_page()
        self.add_partials()
        return self.router
