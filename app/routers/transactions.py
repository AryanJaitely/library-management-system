from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_librarian
from app.models.issued_book import IssueStatus
import app.crud as crud
from app.schemas.issued_book import (
    IssueBookRequest, ReturnBookRequest,
    IssuedBookOut, IssuedBookBrief,
)

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.get("", response_model=dict,
            dependencies=[Depends(get_current_librarian)])
def list_transactions(
    status: IssueStatus | None = None,
    student_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    records, total = crud.get_issued_books(
        db, status=status, student_id=student_id, skip=skip, limit=limit
    )
    return {
        "total": total,
        "data": [
            IssuedBookBrief(
                id=r.id,
                student_id=r.student_id,
                student_name=r.student.name,
                book_id=r.book_id,
                book_title=r.book.title,
                issue_date=r.issue_date,
                due_date=r.due_date,
                return_date=r.return_date,
                fine_amount=r.fine_amount,
                fine_paid=r.fine_paid,
                status=r.status,
            )
            for r in records
        ],
    }


@router.post("/issue", response_model=IssuedBookOut, status_code=201,
             dependencies=[Depends(get_current_librarian)])
def issue_book(data: IssueBookRequest, db: Session = Depends(get_db)):
    return crud.issue_book(db, data)


@router.post("/return/{issue_id}", response_model=IssuedBookOut,
             dependencies=[Depends(get_current_librarian)])
def return_book(
    issue_id: int,
    data: ReturnBookRequest = ReturnBookRequest(),
    db: Session = Depends(get_db),
):
    return crud.return_book(db, issue_id, data)


@router.get("/overdue", response_model=dict,
            dependencies=[Depends(get_current_librarian)])
def list_overdue(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    records, total = crud.get_overdue(db, skip=skip, limit=limit)
    return {
        "total": total,
        "data": [
            IssuedBookBrief(
                id=r.id,
                student_id=r.student_id,
                student_name=r.student.name,
                book_id=r.book_id,
                book_title=r.book.title,
                issue_date=r.issue_date,
                due_date=r.due_date,
                return_date=r.return_date,
                fine_amount=r.fine_amount,
                fine_paid=r.fine_paid,
                status=r.status,
            )
            for r in records
        ],
    }


@router.get("/{issue_id}", response_model=IssuedBookOut,
            dependencies=[Depends(get_current_librarian)])
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    return crud.get_issue_record(db, issue_id)
