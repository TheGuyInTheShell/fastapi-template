from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer #, OAuth2PasswordRequestForm, OAuth2
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db
from schemas.user import RQUser, RSUser, RSUserTokenData, RQUserLogin
from services import auth

# prefix /users
router = APIRouter()

oauth2_schema = OAuth2PasswordBearer('/token')

@router.get("/token")
async def token(token: str = Depends(oauth2_schema)):
    return token

@router.get("/me", response_model=RSUserTokenData)
async def current_user(request: Request):
    try:
        token = request.headers.get("Authorization")
        if not token:
            return HTTPException(status_code=401, detatails="No autorizado", headers={
                    "WWW-Authenticate": "Bearer"
                })
        user_data = auth.decode_token(token)
        return RSUserTokenData(
            id=user_data.id,
            username=user_data.sub,
            role=user_data.role,
            full_name=user_data.full_name,
            email=user_data.email,
        )
    except ValueError as e:
        print(e)
        return "Error"
    
@router.post("/sign-in")
async def sign_in(form_data: RQUserLogin, db: AsyncSession = Depends(get_async_db)):
    print(form_data)
    user = await auth.authenticade_user(db, username=form_data.username, password=form_data.password)
    if not user:
        return {
            "Error": "Usuario no encontrado"
        }
    expires_time = 1200
    access_token = await auth.create_token(data={
        "sub": user.username,
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
    }, expires_time=expires_time)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/sign-up", response_model=RSUser)
async def sign_up(form_sign_up: RQUser, db: AsyncSession = Depends(get_async_db)) -> RSUser | None:
    try:
        exists_user = await auth.get_user(db, username=form_sign_up.username)
        if exists_user:
            return HTTPException(status_code=401, detatails="Nombre de usuario tomado", headers={
                    "WWW-Authenticate": "Bearer"
                })
        user = await auth.create_user(db, user_data=form_sign_up)
        return user
    except ValueError as e:
        print(e)
        return "Error"
        
    
