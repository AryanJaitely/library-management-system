import enum

from sqlalchemy import (
    Column, Integer, ForeignKey, Date, Numeric,
    Enum as SAEnum, DateTime, String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class IssueStatus(str, enum.Enum):
    ISSUED = "issued"
    RETURNED = "returned"
    OVERDUE = "overdue"


class IssuedBook(Base):
    __tablename__ = "issued_books"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(
        Integer,
        ForeignKey("students.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    book_id = Column(
        Integer,
        ForeignKey("books.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=True)
    fine_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    fine_paid = Column(Numeric(10, 2), nullable=False, default=0.00)
    status = Column(
        SAEnum(IssueStatus),
        nullable=False,
        default=IssueStatus.ISSUED,
        index=True,
    )
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    student = relationship("Student", back_populates="issued_books")
    book = relationship("Book", back_populates="issued_books")
