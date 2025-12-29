from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr


class Roles(Enum):
    SUPERADMIN = "SUPERADMIN"


class RQUser(BaseModel):
    username: str
    role: str
    password: str
    email: str
    full_name: str


# PYDANTIC
class RSUser(BaseModel):
    uid: str
    username: str
    full_name: str
    email: EmailStr
    role: str

    otp_enabled: bool = False
    created_at: datetime


class RSUserTokenData(BaseModel):
    uid: str
    username: str
    role: str
    full_name: str
    email: EmailStr
    otp_enabled: bool = False


class INUser(RSUser):
    password: str


class RQUserLogin(BaseModel):
    username: str
    password: str
