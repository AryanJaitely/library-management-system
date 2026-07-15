from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_librarian
import app.crud as crud
from app.schemas.issued_book import LibraryStats, PopularBook, FineReport

router = APIRouter(prefix="/api/reports", tags=["Reports"],
                   dependencies=[Depends(get_current_librarian)])


@router.get("/stats", response_model=LibraryStats)
def library_stats(db: Session = Depends(get_db)):
    return crud.get_library_stats(db)


@router.get("/popular", response_model=List[PopularBook])
def popular_books(
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db),
):
    return crud.get_popular_books(db, limit=limit)


@router.get("/fines", response_model=dict)
def fine_report(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    data = crud.get_fine_report(db, skip=skip, limit=limit)
    return {"total": len(data), "data": data}
