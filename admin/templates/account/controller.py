from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from core.database import get_async_db
from modules.users.models import User
from modules.auth.otp import generate_otp_secret, get_otp_provisioning_uri, generate_qr_code_base64, verify_otp_code
from core.middlewares.role_verify_cookie import ROLE_VERIFY_COOKIE

class InitTemplate:
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates
        self.router = APIRouter()

    def add_page(self):
        @self.router.get("", response_class=HTMLResponse)
        async def account_page(request: Request, db: AsyncSession = Depends(get_async_db)):
            # Get current user from request state (set by middleware)
            if not hasattr(request.state, "user"):
                # Should be handled by dependency, but just in case
                raise HTTPException(status_code=401, detail="Unauthorized")
            
            # Fetch fresh user data including otp_enabled status
            user_data = request.state.user
            query = await User.find_by_colunm(db, "uid", user_data.uid)
            user = query.scalar_one_or_none()
            
            if not user:
                 raise HTTPException(status_code=401, detail="User not found")

            return self.templates.TemplateResponse(
                "pages/account.html",
                context={
                    "request": request,
                    "user": user,
                    "active_tab": "account"
                },
            )

    def add_partials(self):
        @self.router.post("/2fa/setup", response_class=HTMLResponse)
        async def setup_2fa(request: Request, db: AsyncSession = Depends(get_async_db)):
             # Generate secret and QR code
            user_data = request.state.user
            query = await User.find_by_colunm(db, "uid", user_data.uid)
            user = query.scalar_one_or_none()
            
            secret = generate_otp_secret()
            uri = get_otp_provisioning_uri(secret, user.username)
            qr_code = generate_qr_code_base64(uri)
            
            return self.templates.TemplateResponse(
                "partials/account/2fa_setup.html",
                context={
                    "request": request,
                    "secret": secret,
                    "qr_code": qr_code
                }
            )

        @self.router.post("/2fa/enable", response_class=HTMLResponse)
        async def enable_2fa(
            request: Request, 
            otp_code: Annotated[str, Form()], 
            secret: Annotated[str, Form()],
            db: AsyncSession = Depends(get_async_db)
        ):
            user_data = request.state.user
            query = await User.find_by_colunm(db, "uid", user_data.uid)
            user = query.scalar_one_or_none()
            
            if verify_otp_code(secret, otp_code):
                user.otp_secret = secret
                user.otp_enabled = True
                await user.save(db)
                
                # Relod user to be sure
                # Return success state
                return self.templates.TemplateResponse(
                    "partials/account/2fa_status.html",
                    context={"request": request, "user": user, "success_message": "2FA Enabled Successfully"}
                )
            else:
                 # Return error in the setup modal?
                 return self.templates.TemplateResponse(
                    "partials/account/2fa_setup.html",
                    context={
                        "request": request, 
                        "secret": secret, 
                        # Regenerate QR code? Or assume client still has it? 
                        # Ideally we pass error back.
                        # For simplicity, returning the setup view with error.
                        # Use hx-target to replace the modal body.
                         "error": "Invalid Code",
                         # We need to regenerate QR to show it again if we replace the whole body
                         "qr_code": generate_qr_code_base64(get_otp_provisioning_uri(secret, user.username))
                    }
                )

        @self.router.post("/2fa/disable", response_class=HTMLResponse)
        async def disable_2fa(request: Request, db: AsyncSession = Depends(get_async_db)):
            user_data = request.state.user
            query = await User.find_by_colunm(db, "uid", user_data.uid)
            user = query.scalar_one_or_none()
            
            user.otp_enabled = False
            user.otp_secret = None
            await user.save(db)
            
            return self.templates.TemplateResponse(
                "partials/account/2fa_status.html",
                 context={"request": request, "user": user, "success_message": "2FA Disabled"}
            )

    def add_all(self):
        self.add_page()
        self.add_partials()
        return self.router
