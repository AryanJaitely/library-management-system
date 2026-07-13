from typing import List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from fastapi import HTTPException

from app.models.book import Book
from app.models.author import Author
from app.models.category import Category
from app.schemas.book import BookCreate, BookUpdate, BookSearch


def _base_query(db: Session):
    return db.query(Book).options(
        joinedload(Book.author),
        joinedload(Book.category),
    )


def get_books(db: Session, params: BookSearch) -> Tuple[List[Book], int]:
    q = _base_query(db)

    if params.query:
        pattern = f"%{params.query}%"
        q = q.join(Author).filter(
            or_(
                Book.title.ilike(pattern),
                Book.isbn.ilike(pattern),
                Author.name.ilike(pattern),
            )
        )
    if params.author_id:
        q = q.filter(Book.author_id == params.author_id)
    if params.category_id:
        q = q.filter(Book.category_id == params.category_id)
    if params.available_only:
        q = q.filter(Book.available_copies > 0)

    total = q.count()
    books = q.offset(params.skip).limit(params.limit).all()
    return books, total


def get_book(db: Session, book_id: int) -> Book:
    book = _base_query(db).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


def get_book_by_isbn(db: Session, isbn: str) -> Book | None:
    return db.query(Book).filter(Book.isbn == isbn).first()


def create_book(db: Session, data: BookCreate) -> Book:
    if get_book_by_isbn(db, data.isbn):
        raise HTTPException(status_code=400, detail="ISBN already exists")

    # Verify FK references exist
    if not db.query(Author).filter(Author.id == data.author_id).first():
        raise HTTPException(status_code=404, detail="Author not found")
    if not db.query(Category).filter(Category.id == data.category_id).first():
        raise HTTPException(status_code=404, detail="Category not found")

    book = Book(**data.model_dump(), available_copies=data.total_copies)
    db.add(book)
    db.commit()
    db.refresh(book)
    return get_book(db, book.id)


def update_book(db: Session, book_id: int, data: BookUpdate) -> Book:
    book = get_book(db, book_id)
    updates = data.model_dump(exclude_unset=True)

    if "total_copies" in updates:
        new_total = updates["total_copies"]
        issued = book.total_copies - book.available_copies
        if new_total < issued:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reduce total copies below currently issued count ({issued})",
            )
        updates["available_copies"] = new_total - issued

    for field, value in updates.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return get_book(db, book_id)


def delete_book(db: Session, book_id: int) -> dict:
    book = get_book(db, book_id)
    active = [ib for ib in book.issued_books if ib.status.value == "issued"]
    if active:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete book with active issued copies",
        )
    db.delete(book)
    db.commit()
    return {"detail": "Book deleted"}
