from fastapi import Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

class InitTemplate:
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates
        self.router = APIRouter()

    def add_page(self):
        @self.router.get("", response_class=HTMLResponse)
        async def modules_page(request: Request):


            routes = request.app.routes
            
            
            modules = []
            # Process defined
            for route in routes:
                try:
                    name: str = route.__getattribute__('name')
                    methods: set = route.__getattribute__('methods')
                    description: str = route.__getattribute__('path')
                    modules.append({
                            "name": name,
                            "methods": methods,
                            "description": description
                        })
                except Exception as e:
                    print(e)
                    continue    
            
            return self.templates.TemplateResponse(
                "pages/modules.html",
                context={
                    "request": request,
                    "modules": modules,
                },
            )

    def add_all(self):
        self.add_page()
        return self.router
