from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_librarian
import app.crud as crud
from app.schemas.student import StudentCreate, StudentUpdate, StudentOut
from app.schemas.issued_book import IssuedBookBrief

router = APIRouter(prefix="/api/students", tags=["Students"])


@router.get("", response_model=dict,
            dependencies=[Depends(get_current_librarian)])
def list_students(
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    students, total = crud.get_students(db, skip=skip, limit=limit, search=search)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": [StudentOut.model_validate(s) for s in students],
    }


@router.post("", response_model=StudentOut, status_code=201,
             dependencies=[Depends(get_current_librarian)])
def create_student(data: StudentCreate, db: Session = Depends(get_db)):
    return crud.create_student(db, data)


@router.get("/{student_id}", response_model=StudentOut,
            dependencies=[Depends(get_current_librarian)])
def get_student(student_id: int, db: Session = Depends(get_db)):
    return crud.get_student(db, student_id)


@router.put("/{student_id}", response_model=StudentOut,
            dependencies=[Depends(get_current_librarian)])
def update_student(student_id: int, data: StudentUpdate, db: Session = Depends(get_db)):
    return crud.update_student(db, student_id, data)


@router.delete("/{student_id}", dependencies=[Depends(get_current_librarian)])
def delete_student(student_id: int, db: Session = Depends(get_db)):
    return crud.delete_student(db, student_id)


@router.get("/{student_id}/history", response_model=dict,
            dependencies=[Depends(get_current_librarian)])
def student_history(
    student_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    records, total = crud.get_student_history(db, student_id, skip=skip, limit=limit)
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
