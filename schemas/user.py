from pydantic import BaseModel, EmailStr
from enum import Enum

class Roles(Enum):
    SUPERADMIN = "SUPERADMIN"

class RQUser(BaseModel):
    username: str
    password: str
    full_name: str
    email: EmailStr
    role: Roles

# PYDANTIC
class RSUser(BaseModel):
    id: int
    username: str
    full_name: str
    email: EmailStr
    disable: bool
    role: str

class RSUserTokenData(BaseModel):
    id: int
    username: str
    role: str
    full_name: str
    email: EmailStr


class INUser(RSUser):
    password: str
    
class RQUserLogin(BaseModel):
    username: str
    password: str