from typing import Annotated

from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from modules.auth.services import authenticade_user, create_token


class InitTemplate:
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates
        self.router = APIRouter()

    def add_page(self):

        @self.router.get("", response_class=HTMLResponse)
        async def main_sign_in(request: Request):
            return self.templates.TemplateResponse(
                "pages/sign-in.html",
                context={
                    "request": request,
                },
            )

    def add_partials(self):

        @self.router.post("/partial/sign-in", response_class=HTMLResponse)
        async def sign_in(
            request: Request,
            username: Annotated[str, Form()],
            password: Annotated[str, Form()],
            db: AsyncSession = Depends(get_async_db),
        ):

            try:
                user = await authenticade_user(db, username=username, password=password)
                if user is None:
                    raise HTTPException(
                        status_code=401, detail="Incorrect username or password"
                    )
                expires_time = 1200
                access_token = create_token(
                    data={
                        "sub": user.username,
                        "email": user.email,
                        "role": user.role,
                        "full_name": user.full_name,
                        "id": user.uid,
                    },
                    expires_time=expires_time,
                )

                response = self.templates.TemplateResponse(
                    f"partials/sign-in.html",
                    context={"request": request, "success": True},
                )
                response.set_cookie(
                    key="access_token",
                    value=access_token,
                    httponly=True,
                    secure=True,
                    samesite="strict",
                )
                return response
            except HTTPException as e:
                print(e)
                response = self.templates.TemplateResponse(
                    f"partials/sign-in.html",
                    context={"request": request, "success": False, "detail": e.detail},
                )
                return response

    def add_all(self):
        self.add_page()
        self.add_partials()
        return self.router
