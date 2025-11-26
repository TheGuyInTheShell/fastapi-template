from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates

from core.database.base import BaseAsync
from core.utils.mermaid import generate_mermaid_diagram


class InitTemplate:
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates
        self.router = APIRouter()

    def add_page(self):
        @self.router.get("", response_class=HTMLResponse)
        async def models_diagram_page(request: Request):
            # Generate the Mermaid diagram syntax
            diagram_syntax = generate_mermaid_diagram(BaseAsync)
            
            return self.templates.TemplateResponse(
                "pages/models_diagram.html",
                context={
                    "request": request,
                    "diagram_syntax": diagram_syntax,
                },
            )

    def add_partials(self):
        # No partials needed for this page
        pass

    def add_all(self):
        self.add_page()
        self.add_partials()
        return self.router
