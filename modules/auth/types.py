from pydantic import BaseModel


class TokenData(BaseModel):
    sub: str
    email: str
    id: str
    role: str
    full_name: str
    exp: str
    iat: str
    jti: str
    iss: str