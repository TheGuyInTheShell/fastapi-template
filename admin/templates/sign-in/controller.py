from typing import Annotated

from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.users.models import User
from app.modules.auth.services import decode_token


from core.database import get_async_db
from app.modules.auth.services import (
    authenticade_user,
    create_token,
    create_refresh_token,
    REFRESH_TOKEN_EXPIRE_MINUTES,
)
from .services import has_permission


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
        async def admin_sign_in(
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

                if not await has_permission(db, user.role, "admin_sign_in", "POST"):
                    raise HTTPException(
                        status_code=401, detail="You do not have permission to sign in"
                    )

                if user.otp_enabled:
                    # Issue temp token
                    temp_token = create_token(
                        data={
                            "sub": user.username,
                            "id": user.id,
                            "type": "partial_2fa",
                            "role": "guest"
                        }, 
                        expires_time=300
                    )
                    
                    return self.templates.TemplateResponse(
                        "partials/sign-in-otp.html",
                        context={
                            "request": request,
                            "temp_token": temp_token
                        }
                    )

                expires_time = 1200
                access_token = create_token(
                    data={
                        "sub": user.username,
                        "email": user.email,
                        "role": user.role,
                        "full_name": user.full_name,
                        "id": user.id,
                    },
                    expires_time=expires_time,
                )

                refresh_token = create_refresh_token(
                    data={
                        "sub": user.username,
                        "email": user.email,
                        "role": user.role,
                        "full_name": user.full_name,
                        "id": user.id,
                    }
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
                    samesite="lax",
                )
                response.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    httponly=True,
                    secure=True,
                    samesite="lax",
                    path="/auth/refresh",
                )
                return response
            except HTTPException as e:
                print(e)
                response = self.templates.TemplateResponse(
                    f"partials/sign-in.html",
                    context={"request": request, "success": False, "detail": e.detail},
                )
                return response

        @self.router.post("/partial/verify-otp", response_class=HTMLResponse)
        async def admin_verify_otp(
            request: Request,
            otp_code: Annotated[str, Form()],
            temp_token: Annotated[str, Form()],
            db: AsyncSession = Depends(get_async_db),
        ):
            try:
                payload = decode_token(temp_token)
                
                if not payload or payload.type != "partial_2fa":
                    raise HTTPException(status_code=401, detail="Invalid session")
                
                user_id = payload.id
                if user_id is None:
                    raise HTTPException(status_code=401, detail="Invalid session")

                user = await User.find_one(db, user_id)
                
                if not user:
                    raise HTTPException(status_code=401, detail="User not found")
                
                if not user.otp_enabled:
                    raise HTTPException(status_code=400, detail="2FA not enabled")

                # 3. Verify OTP
                from app.modules.auth.otp import verify_otp_code
                if not verify_otp_code(user.otp_secret, otp_code):
                     raise HTTPException(status_code=401, detail="Invalid Code")

                # 4. Issue Tokens
                expires_time = 1200
                access_token = create_token(
                    data={
                        "sub": user.username,
                        "email": user.email,
                        "role": user.role_ref,
                        "full_name": user.full_name,
                        "id": user.id,
                    },
                    expires_time=expires_time,
                )

                refresh_token = create_refresh_token(
                    data={
                        "sub": user.username,
                        "email": user.email,
                        "role": user.role_ref,
                        "full_name": user.full_name,
                        "id": user.id,
                    }
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
                    samesite="lax",
                )
                response.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    httponly=True,
                    secure=True,
                    samesite="lax",
                    path="/auth/refresh",
                )
                return response

            except HTTPException as e:
                response = self.templates.TemplateResponse(
                    f"partials/sign-in.html",
                    context={"request": request, "success": False, "detail": e.detail},
                )
                return response


    def add_all(self) -> APIRouter:
        self.add_page()
        self.add_partials()
        return self.router
