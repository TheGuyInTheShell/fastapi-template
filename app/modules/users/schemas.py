from datetime import datetime
from enum import Enum
from typing import Union

from pydantic import BaseModel, EmailStr


class Roles(Enum):
    SUPERADMIN = "SUPERADMIN"


class RQUser(BaseModel):
    username: str
    role: Union[int, str]
    password: str
    email: str
    full_name: str


# PYDANTIC
class RSUser(BaseModel):
    id: Union[int, str]
    username: str
    full_name: str
    email: EmailStr
    role: Union[int, str]

    otp_enabled: bool = False
    created_at: datetime


class RSUserTokenData(BaseModel):
    id: Union[int, str]
    uid: Union[int, str]
    username: str
    role: Union[int, str]
    full_name: str
    email: EmailStr
    otp_enabled: bool = False


class INUser(RSUser):
    password: str


class RQUserLogin(BaseModel):
    username: str
    password: str
