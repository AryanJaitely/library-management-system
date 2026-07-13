from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_librarian
import app.crud as crud
from app.schemas.book import BookCreate, BookUpdate, BookOut, BookSearch

router = APIRouter(prefix="/api/books", tags=["Books"])


@router.get("", response_model=dict)
def list_books(
    query: str | None = Query(None, description="Search title, ISBN, author"),
    author_id: int | None = None,
    category_id: int | None = None,
    available_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    params = BookSearch(
        query=query,
        author_id=author_id,
        category_id=category_id,
        available_only=available_only,
        skip=skip,
        limit=limit,
    )
    books, total = crud.get_books(db, params)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": [BookOut.model_validate(b) for b in books],
    }


@router.post("", response_model=BookOut, status_code=201,
             dependencies=[Depends(get_current_librarian)])
def create_book(data: BookCreate, db: Session = Depends(get_db)):
    return crud.create_book(db, data)


@router.get("/{book_id}", response_model=BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)):
    return crud.get_book(db, book_id)


@router.put("/{book_id}", response_model=BookOut,
            dependencies=[Depends(get_current_librarian)])
def update_book(book_id: int, data: BookUpdate, db: Session = Depends(get_db)):
    return crud.update_book(db, book_id, data)


@router.delete("/{book_id}", dependencies=[Depends(get_current_librarian)])
def delete_book(book_id: int, db: Session = Depends(get_db)):
    return crud.delete_book(db, book_id)
