from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel

from app.models.issued_book import IssueStatus
from app.schemas.book import BookOut
from app.schemas.student import StudentOut


class IssueBookRequest(BaseModel):
    student_id: int
    book_id: int
    notes: Optional[str] = None
    # Override default due date (optional)
    due_date: Optional[date] = None


class ReturnBookRequest(BaseModel):
    return_date: Optional[date] = None   # defaults to today
    fine_paid: Optional[Decimal] = None  # amount paid at return


class IssuedBookOut(BaseModel):
    id: int
    student: StudentOut
    book: BookOut
    issue_date: date
    due_date: date
    return_date: Optional[date]
    fine_amount: Decimal
    fine_paid: Decimal
    status: IssueStatus
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class IssuedBookBrief(BaseModel):
    """Lightweight version for list views."""
    id: int
    student_id: int
    student_name: str
    book_id: int
    book_title: str
    issue_date: date
    due_date: date
    return_date: Optional[date]
    fine_amount: Decimal
    fine_paid: Decimal
    status: IssueStatus

    model_config = {"from_attributes": True}


# ── Report schemas ────────────────────────────────────────────────────────────

class LibraryStats(BaseModel):
    total_books: int
    total_copies: int
    available_copies: int
    total_students: int
    active_issues: int
    overdue_issues: int
    total_fines_pending: Decimal
    total_fines_collected: Decimal


class PopularBook(BaseModel):
    book_id: int
    title: str
    author: str
    borrow_count: int


class FineReport(BaseModel):
    student_id: int
    student_name: str
    enrollment_no: str
    total_fine: Decimal
    fine_paid: Decimal
    fine_pending: Decimal
