from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr


class Roles(Enum):
    SUPERADMIN = "SUPERADMIN"

class RQUser(BaseModel):
    username: str
    role: str
    password: str
    email: EmailStr
    full_name: str

# PYDANTIC
class RSUser(BaseModel):
    uid: str
    username: str
    full_name: str | None = None
    email: EmailStr 
    role: str

    def email_is_empty(self):
        return self.email is None

class RSUserTokenData(BaseModel):
    uid: str
    username: str
    role: str
    full_name: str | None = None
    email: EmailStr


class INUser(RSUser):
    password: str


    
class RQUserLogin(BaseModel):
    username: str
    password: str