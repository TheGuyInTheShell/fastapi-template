from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates


class InitTemplate:
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates
        self.router = APIRouter()

    def add_all(self) -> APIRouter:
        @self.router.get("")
        async def logout(request: Request):
            response = RedirectResponse(url="/admin/sign-in", status_code=302)
            response.delete_cookie(key="access_token")
            return response

        return self.router
