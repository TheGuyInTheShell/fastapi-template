from fastapi import HTTPException, Request, status

from modules.auth.schemas import RSUser
from modules.auth.services import decode_token


async def JWT_VERIFY(jwt: str) -> RSUser:
    try:
        if not jwt:
            raise ValueError("JWT not found")
        payload = decode_token(jwt)
        if not payload:
            raise ValueError("JWT invalid")
        return payload
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )