from fastapi import Request
from fastapi import HTTPException, status
from services import auth
from schemas.user import RSUser

async def JWT_VERIFY(request: Request) -> RSUser:
    try:
        jwt = request.headers.get('Authorization').split(' ')[1]
        if not jwt:
            raise ValueError("JWT not found")
        payload = auth.decode_token(jwt)
        if not payload:
            raise ValueError("JWT invalid")
        return payload
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )