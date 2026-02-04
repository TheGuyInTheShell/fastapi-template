from pydantic import BaseModel


class TokenData(BaseModel):
    sub: str
    email: str | None = None
    id: int | str | None = None
    uid: str | None = None
    role: int | str | None = None
    full_name: str | None = None
    exp: float | int | None = None
    iat: float | int | None = None
    jti: str | None = None
    iss: str | None = None
    type: str | None = None
    otp_enabled: bool = False
