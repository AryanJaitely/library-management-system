from pydantic import BaseModel, EmailStr
from typing import Optional


class LibrarianCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class LibrarianOut(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None
