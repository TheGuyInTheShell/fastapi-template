from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates


class InitTemplate:
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates
        self.router = APIRouter()

    def add_page(self):

        @self.router.get("", response_class=HTMLResponse)
        async def main_dashboard(request: Request):
            return self.templates.TemplateResponse(
                "pages/dashboard.html",
                context={
                    "request": request,
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
