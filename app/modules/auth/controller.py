from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from app.modules.users.models import User

from .schemas import RQUser, RQUserLogin, RSUser, RSUserTokenData, OTPEnableRequest
from .types import TokenData
from .services import (
    authenticade_user,
    create_refresh_token,
    create_token,
    create_user,
    decode_token,
    get_user,
    get_user,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    get_current_user
)
from .otp import generate_otp_secret, verify_otp_code, get_otp_provisioning_uri, generate_qr_code_base64
from pydantic import BaseModel

# prefix /auth
router = APIRouter()

oauth2_schema = OAuth2PasswordBearer("auth/sign-in")
tag = "auth"


@router.get("/", tags=[tag])
def token(token: str = Depends(oauth2_schema)):
    return token


@router.post("/sign-in", tags=[tag])
async def sign_in(user_data: RQUserLogin, db: AsyncSession = Depends(get_async_db)):
    try:
        user = await authenticade_user(
            db, username=user_data.username, password=user_data.password
        )
        if user is None:
            raise HTTPException(
                status_code=401, detail="Incorrect username or password"
            )

        if user.otp_enabled:
             # Create a temporary partial token or just return a signal
             # Ideally we issue a temporary token with a "partial_auth" scope or similar.
             # For simplicity, we can return a specific response that client handles.
             # Let's issue a temporary token that is ONLY valid for verifying OTP.
             temp_token = create_token(
                data={
                    "sub": user.username,
                    "id": user.uid,
                    "type": "partial_2fa",
                     # Short expiry for this step
                    "role": "guest" # No permissions
                }, 
                expires_time=300 # 5 minutes
             )
             return JSONResponse(
                 status_code=202, # Accepted
                 content={
                     "message": "OTP required",
                     "temp_token": temp_token,
                     "require_2fa": True
                 }
             )

        # Create access token
        access_token = create_token(
            data={
                "sub": user.username,
                "email": user.email,
                "role": user.role,
                "full_name": user.full_name,
                "id": user.uid,
            }
        )

        # Create refresh token
        refresh_token = create_refresh_token(
            data={
                "sub": user.username,
                "email": user.email,
                "role": user.role,
                "full_name": user.full_name,
                "id": user.uid,
            }
        )

        # Create response with JWTs in body (optional for refresh_token, but useful)
        response = JSONResponse(
            content={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
        )

        # Set Access Token in HTTP-only cookie (existing behavior)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            # max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60, # Use if imported or hardcode
            samesite="lax",
            # secure=True,
        )

        # Set Refresh Token in HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60,
            path="/auth/refresh",
            samesite="lax",
            # secure=True,
        )

        return response
    except ValueError as e:
        print(e)
        raise e


@router.post("/refresh", tags=[tag])
async def refresh_token_endpoint(
    request: Request, response: Response, refresh_token: Optional[str] = Cookie(None)
):
    if not refresh_token:
        # Also check Authorization header or body if needed, but cookie is primary
        raise HTTPException(status_code=401, detail="Refresh token missing")

    token_data = decode_token(refresh_token)

    # decode_token returns a dict or TokenData. Based on services.py it returns jwt.decode result which is dict but typed as TokenData.
    # Let's assume dict access for safety or convert to model.
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if token_data.type != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    # Allow token rotation? For now just issue new access token.
    # We can also issue a new refresh token if we want to rotate them.

    # Extract user data
    username = token_data.sub
    email = token_data.email
    role = token_data.role
    full_name = token_data.full_name
    uid = token_data.id

    new_access_token = create_token(
        data={
            "sub": username,
            "email": email,
            "role": role,
            "full_name": full_name,
            "id": uid,
        }
    )

    response = JSONResponse(
        content={"access_token": new_access_token, "token_type": "bearer"}
    )

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        samesite="lax",
    )

    return response


class OTPVerifyRequest(BaseModel):
    otp_code: str
    temp_token: str

@router.post("/verify-otp", tags=[tag])
async def verify_otp(request: OTPVerifyRequest, db: AsyncSession = Depends(get_async_db)):
    # Decode temp token
    payload = decode_token(request.temp_token)
    if not payload or payload.type != "partial_2fa":
        raise HTTPException(status_code=401, detail="Invalid session")
    
    uid = payload.id
    user_query = await User.find_by_colunm(db, "uid", uid)
    user = user_query.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    if not user.otp_enabled:
         # Weird state, maybe 2FA was disabled in between?
         raise HTTPException(status_code=400, detail="2FA not enabled for user")

    if not verify_otp_code(user.otp_secret, request.otp_code):
        raise HTTPException(status_code=401, detail="Invalid OTP code")
        
    # Issue full tokens
    access_token = create_token(
            data={
                "sub": user.username,
                "email": user.email,
                "role": user.role,
                "full_name": user.full_name,
                "id": user.uid,
            }
        )
    
    refresh_token = create_refresh_token(
            data={
                "sub": user.username,
                "email": user.email,
                "role": user.role,
                "full_name": user.full_name,
                "id": user.uid,
            }
        )

    response = JSONResponse(
            content={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
        )

    response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="lax",
        )

    response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60,
            path="/auth/refresh",
            samesite="lax",
        )
        
    return response


@router.get("/2fa/setup", tags=[tag])
async def setup_2fa(current_user=Depends(get_current_user)):
    secret = generate_otp_secret()
    uri = get_otp_provisioning_uri(secret, current_user.username)
    qr_b64 = generate_qr_code_base64(uri)
    
    return {
        "secret": secret,
        "qr_code": qr_b64
    }


@router.post("/2fa/enable", tags=[tag])
async def enable_2fa(request: OTPEnableRequest, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    if verify_otp_code(request.secret, request.otp_code):
        current_user.otp_secret = request.secret
        current_user.otp_enabled = True
        await current_user.save(db)
        return {"message": "2FA enabled successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP code")

@router.post("/2fa/disable", tags=[tag])
async def disable_2fa(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    current_user.otp_enabled = False
    current_user.otp_secret = None
    await current_user.save(db)
    return {"message": "2FA disabled successfully"}


@router.post("/sign-up", response_model=RSUser, tags=[tag])
async def sign_up(
    form_sign_up: RQUser, db: AsyncSession = Depends(get_async_db)
) -> RSUser | None:
    try:
        query = await User.find_by_colunm(db, "username", form_sign_up.username)
        exists_user = query.scalar_one_or_none()
        if exists_user:
            raise HTTPException(
                status_code=401,
                detail="Nombre de usuario tomado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        result = await create_user(db, form_sign_up)
        if not result:
            raise HTTPException(status_code=500, detail="Error al crear el usuario")
        return RSUser(
            uid=result.get("uid") or "",
            username=result.get("username") or "",
            role=result.get("role") or "",
            full_name=result.get("full_name") or "",
            email=result.get("email") or "",
        )
    except ValueError as e:
        print(e)
        raise e
