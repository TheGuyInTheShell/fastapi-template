from datetime import datetime
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, EmailStr


class Roles(Enum):
    SUPERADMIN = "SUPERADMIN"


class RQUser(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str


# PYDANTIC
class RSUser(BaseModel):
    uid: Union[int, str]
    id: Union[int, str]
    username: str
    full_name: str | None = None
    email: EmailStr
    role: int | str
    otp_enabled: bool = False

    def email_is_empty(self):
        return self.email is None


class RSUserTokenData(BaseModel):
    uid: Union[int, str]
    id: Union[int, str]
    username: str
    role: int | str
    full_name: str | None = None
    email: EmailStr
    otp_enabled: bool = False


class INUser(RSUser):
    password: str


class RQUserLogin(BaseModel):
    username: str
    password: str

class OTPEnableRequest(BaseModel):
    otp_code: str
    secret: str
