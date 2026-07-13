from typing import Optional
from pydantic import BaseModel, field_validator

from app.schemas.author_category import AuthorOut, CategoryOut


class BookBase(BaseModel):
    title: str
    isbn: str
    description: Optional[str] = None
    total_copies: int = 1
    author_id: int
    category_id: int

    @field_validator("total_copies")
    @classmethod
    def copies_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("total_copies must be at least 1")
        return v


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    total_copies: Optional[int] = None
    author_id: Optional[int] = None
    category_id: Optional[int] = None


class BookOut(BaseModel):
    id: int
    title: str
    isbn: str
    description: Optional[str]
    total_copies: int
    available_copies: int
    author: AuthorOut
    category: CategoryOut

    model_config = {"from_attributes": True}


class BookSearch(BaseModel):
    """Query params for book search."""
    query: Optional[str] = None       # searches title + isbn
    author_id: Optional[int] = None
    category_id: Optional[int] = None
    available_only: bool = False
    skip: int = 0
    limit: int = 20
