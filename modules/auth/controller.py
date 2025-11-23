from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from modules.users.models import User

from .schemas import RQUser, RQUserLogin, RSUser, RSUserTokenData
from .services import authenticade_user, create_token, create_user, get_user

# prefix /auth
router = APIRouter()

oauth2_schema = OAuth2PasswordBearer("auth/sign-in")
tag = 'auth'

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
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError as e:
        print(e)
        raise e


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
        return result
    except ValueError as e:
        print(e)
        raise e
