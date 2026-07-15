from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_librarian
import app.crud as crud
from app.schemas.author_category import (
    AuthorCreate, AuthorUpdate, AuthorOut,
    CategoryCreate, CategoryUpdate, CategoryOut,
)

router = APIRouter(tags=["Authors & Categories"])


# ── Authors ──────────────────────────────────────────────────────────────────

@router.get("/api/authors", response_model=List[AuthorOut])
def list_authors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=200),
    db: Session = Depends(get_db),
):
    return crud.get_authors(db, skip=skip, limit=limit)


@router.post("/api/authors", response_model=AuthorOut, status_code=201,
             dependencies=[Depends(get_current_librarian)])
def create_author(data: AuthorCreate, db: Session = Depends(get_db)):
    return crud.create_author(db, data)


@router.get("/api/authors/{author_id}", response_model=AuthorOut)
def get_author(author_id: int, db: Session = Depends(get_db)):
    return crud.get_author(db, author_id)


@router.put("/api/authors/{author_id}", response_model=AuthorOut,
            dependencies=[Depends(get_current_librarian)])
def update_author(author_id: int, data: AuthorUpdate, db: Session = Depends(get_db)):
    return crud.update_author(db, author_id, data)


@router.delete("/api/authors/{author_id}",
               dependencies=[Depends(get_current_librarian)])
def delete_author(author_id: int, db: Session = Depends(get_db)):
    return crud.delete_author(db, author_id)


# ── Categories ────────────────────────────────────────────────────────────────

@router.get("/api/categories", response_model=List[CategoryOut])
def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=200),
    db: Session = Depends(get_db),
):
    return crud.get_categories(db, skip=skip, limit=limit)


@router.post("/api/categories", response_model=CategoryOut, status_code=201,
             dependencies=[Depends(get_current_librarian)])
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    return crud.create_category(db, data)


@router.get("/api/categories/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return crud.get_category(db, category_id)


@router.put("/api/categories/{category_id}", response_model=CategoryOut,
            dependencies=[Depends(get_current_librarian)])
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    return crud.update_category(db, category_id, data)


@router.delete("/api/categories/{category_id}",
               dependencies=[Depends(get_current_librarian)])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    return crud.delete_category(db, category_id)
