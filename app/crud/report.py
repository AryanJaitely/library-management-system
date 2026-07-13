from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.book import Book
from app.models.student import Student
from app.models.issued_book import IssuedBook, IssueStatus
from app.models.author import Author
from app.schemas.issued_book import LibraryStats, PopularBook, FineReport


def get_library_stats(db: Session) -> LibraryStats:
    total_books = db.query(func.count(Book.id)).scalar() or 0
    total_copies = db.query(func.coalesce(func.sum(Book.total_copies), 0)).scalar() or 0
    available_copies = db.query(func.coalesce(func.sum(Book.available_copies), 0)).scalar() or 0
    total_students = db.query(func.count(Student.id)).scalar() or 0

    active_issues = db.query(func.count(IssuedBook.id)).filter(
        IssuedBook.status == IssueStatus.ISSUED
    ).scalar() or 0

    overdue_issues = db.query(func.count(IssuedBook.id)).filter(
        IssuedBook.status == IssueStatus.OVERDUE
    ).scalar() or 0

    total_fines_pending = db.query(
        func.coalesce(
            func.sum(IssuedBook.fine_amount - IssuedBook.fine_paid), 0
        )
    ).filter(IssuedBook.status == IssueStatus.OVERDUE).scalar() or Decimal("0")

    total_fines_collected = db.query(
        func.coalesce(func.sum(IssuedBook.fine_paid), 0)
    ).scalar() or Decimal("0")

    return LibraryStats(
        total_books=total_books,
        total_copies=int(total_copies),
        available_copies=int(available_copies),
        total_students=total_students,
        active_issues=active_issues,
        overdue_issues=overdue_issues,
        total_fines_pending=Decimal(str(total_fines_pending)),
        total_fines_collected=Decimal(str(total_fines_collected)),
    )


def get_popular_books(db: Session, limit: int = 10):
    rows = (
        db.query(
            Book.id,
            Book.title,
            Author.name.label("author"),
            func.count(IssuedBook.id).label("borrow_count"),
        )
        .join(IssuedBook, IssuedBook.book_id == Book.id)
        .join(Author, Author.id == Book.author_id)
        .group_by(Book.id, Book.title, Author.name)
        .order_by(desc("borrow_count"))
        .limit(limit)
        .all()
    )
    return [
        PopularBook(book_id=r.id, title=r.title, author=r.author, borrow_count=r.borrow_count)
        for r in rows
    ]


def get_fine_report(db: Session, skip: int = 0, limit: int = 20):
    rows = (
        db.query(
            Student.id,
            Student.name,
            Student.enrollment_no,
            func.coalesce(func.sum(IssuedBook.fine_amount), 0).label("total_fine"),
            func.coalesce(func.sum(IssuedBook.fine_paid), 0).label("fine_paid"),
        )
        .join(IssuedBook, IssuedBook.student_id == Student.id)
        .filter(IssuedBook.fine_amount > 0)
        .group_by(Student.id, Student.name, Student.enrollment_no)
        .order_by(desc("total_fine"))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        FineReport(
            student_id=r.id,
            student_name=r.name,
            enrollment_no=r.enrollment_no,
            total_fine=Decimal(str(r.total_fine)),
            fine_paid=Decimal(str(r.fine_paid)),
            fine_pending=Decimal(str(r.total_fine)) - Decimal(str(r.fine_paid)),
        )
        for r in rows
    ]
