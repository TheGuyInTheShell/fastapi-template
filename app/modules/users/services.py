from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User
from app.modules.users.schemas import RSUser
from app.modules.auth.services import decode_token
from core.database import get_async_db
from fastapi.security import OAuth2PasswordBearer

oauth2_schema = OAuth2PasswordBearer("auth/sign-in")


async def get_current_user(
    token: str = Depends(oauth2_schema), 
    db: AsyncSession = Depends(get_async_db)
) -> RSUser:
    """
    Obtiene el usuario actual desde el token JWT de la request.
    
    Args:
        token: Token JWT del usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        RSUser: Schema Pydantic con los datos del usuario
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    # Decodificar el token JWT
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    # Buscar el usuario en la base de datos
    query = await User.find_by_colunm(db, "username", payload.sub)
    user = query.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    # Retornar el schema Pydantic con los datos del usuario
    return RSUser(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        role=user.role_ref,
        otp_enabled=user.otp_enabled,
        created_at=user.created_at,
    )
