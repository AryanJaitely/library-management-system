from datetime import date, timedelta
from decimal import Decimal
from typing import List, Tuple

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException

from app.models.issued_book import IssuedBook, IssueStatus
from app.models.book import Book
from app.models.student import Student
from app.schemas.issued_book import IssueBookRequest, ReturnBookRequest
from app.core.config import settings


def _load_issued(db: Session):
    return db.query(IssuedBook).options(
        joinedload(IssuedBook.student),
        joinedload(IssuedBook.book).joinedload(Book.author),
        joinedload(IssuedBook.book).joinedload(Book.category),
    )


def _calculate_fine(due_date: date, return_date: date) -> Decimal:
    days_late = (return_date - due_date).days
    if days_late <= 0:
        return Decimal("0.00")
    return Decimal(str(round(days_late * settings.FINE_PER_DAY, 2)))


def issue_book(db: Session, data: IssueBookRequest) -> IssuedBook:
    # Validate student exists
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Validate book exists and has copies
    book = db.query(Book).filter(Book.id == data.book_id).with_for_update().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.available_copies < 1:
        raise HTTPException(status_code=400, detail="No copies available for this book")

    # Check student doesn't already have this book issued
    already = db.query(IssuedBook).filter(
        IssuedBook.student_id == data.student_id,
        IssuedBook.book_id == data.book_id,
        IssuedBook.status == IssueStatus.ISSUED,
    ).first()
    if already:
        raise HTTPException(status_code=400, detail="Student already has this book issued")

    today = date.today()
    due = data.due_date or today + timedelta(days=settings.DEFAULT_BORROW_DAYS)

    issued = IssuedBook(
        student_id=data.student_id,
        book_id=data.book_id,
        issue_date=today,
        due_date=due,
        status=IssueStatus.ISSUED,
        notes=data.notes,
    )
    book.available_copies -= 1

    db.add(issued)
    db.commit()
    db.refresh(issued)
    return _load_issued(db).filter(IssuedBook.id == issued.id).first()


def return_book(db: Session, issue_id: int, data: ReturnBookRequest) -> IssuedBook:
    issued = db.query(IssuedBook).filter(IssuedBook.id == issue_id).with_for_update().first()
    if not issued:
        raise HTTPException(status_code=404, detail="Issue record not found")
    if issued.status == IssueStatus.RETURNED:
        raise HTTPException(status_code=400, detail="Book already returned")

    return_date = data.return_date or date.today()
    fine = _calculate_fine(issued.due_date, return_date)

    issued.return_date = return_date
    issued.fine_amount = fine
    issued.fine_paid = data.fine_paid or Decimal("0.00")
    issued.status = IssueStatus.RETURNED

    # Increment available copies
    book = db.query(Book).filter(Book.id == issued.book_id).with_for_update().first()
    book.available_copies += 1

    db.commit()
    db.refresh(issued)
    return _load_issued(db).filter(IssuedBook.id == issued.id).first()


def get_issued_books(
    db: Session,
    status: IssueStatus | None = None,
    student_id: int | None = None,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[IssuedBook], int]:
    q = _load_issued(db)
    if status:
        q = q.filter(IssuedBook.status == status)
    if student_id:
        q = q.filter(IssuedBook.student_id == student_id)

    # Auto-flag overdue records
    _sync_overdue(db)

    total = q.count()
    return q.order_by(IssuedBook.due_date.asc()).offset(skip).limit(limit).all(), total


def get_issue_record(db: Session, issue_id: int) -> IssuedBook:
    record = _load_issued(db).filter(IssuedBook.id == issue_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Issue record not found")
    return record


def get_overdue(db: Session, skip: int = 0, limit: int = 20) -> Tuple[List[IssuedBook], int]:
    _sync_overdue(db)
    today = date.today()
    q = _load_issued(db).filter(
        IssuedBook.status == IssueStatus.OVERDUE,
        IssuedBook.due_date < today,
    )
    total = q.count()
    return q.order_by(IssuedBook.due_date.asc()).offset(skip).limit(limit).all(), total


def get_student_history(
    db: Session,
    student_id: int,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[IssuedBook], int]:
    if not db.query(Student).filter(Student.id == student_id).first():
        raise HTTPException(status_code=404, detail="Student not found")
    q = _load_issued(db).filter(IssuedBook.student_id == student_id)
    total = q.count()
    return q.order_by(IssuedBook.issue_date.desc()).offset(skip).limit(limit).all(), total


def _sync_overdue(db: Session) -> None:
    """Mark ISSUED records past due_date as OVERDUE (lightweight bulk update)."""
    today = date.today()
    db.query(IssuedBook).filter(
        IssuedBook.status == IssueStatus.ISSUED,
        IssuedBook.due_date < today,
    ).update({"status": IssueStatus.OVERDUE}, synchronize_session=False)
    db.commit()
