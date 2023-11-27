from schemas.user import RSUser
from fastapi import HTTPException, status, Request
from .jwt_verify import JWT_VERIFY

def ROLE_VERIFY(roles: list[str]) -> RSUser:
    async def INTERNAL_ROLE_VERIFY(request: Request):
        payload = await JWT_VERIFY(request)
        if payload.role in roles:
            return payload
        else:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return INTERNAL_ROLE_VERIFY