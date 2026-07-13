from typing import Optional
from pydantic import BaseModel


# ── Author ──────────────────────────────────────────────────────────────────

class AuthorBase(BaseModel):
    name: str
    bio: Optional[str] = None


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None


class AuthorOut(AuthorBase):
    id: int

    model_config = {"from_attributes": True}


# ── Category ─────────────────────────────────────────────────────────────────

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryOut(CategoryBase):
    id: int

    model_config = {"from_attributes": True}
