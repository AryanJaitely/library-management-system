from typing import List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate


def get_students(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    search: str | None = None,
) -> Tuple[List[Student], int]:
    q = db.query(Student)
    if search:
        pattern = f"%{search}%"
        q = q.filter(
            Student.name.ilike(pattern)
            | Student.email.ilike(pattern)
            | Student.enrollment_no.ilike(pattern)
        )
    total = q.count()
    return q.offset(skip).limit(limit).all(), total


def get_student(db: Session, student_id: int) -> Student:
    s = db.query(Student).filter(Student.id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    return s


def get_student_by_enrollment(db: Session, enrollment_no: str) -> Student | None:
    return db.query(Student).filter(Student.enrollment_no == enrollment_no).first()


def create_student(db: Session, data: StudentCreate) -> Student:
    if db.query(Student).filter(Student.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if get_student_by_enrollment(db, data.enrollment_no):
        raise HTTPException(status_code=400, detail="Enrollment number already exists")

    student = Student(**data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def update_student(db: Session, student_id: int, data: StudentUpdate) -> Student:
    student = get_student(db, student_id)
    updates = data.model_dump(exclude_unset=True)

    if "email" in updates:
        clash = db.query(Student).filter(
            Student.email == updates["email"],
            Student.id != student_id,
        ).first()
        if clash:
            raise HTTPException(status_code=400, detail="Email already in use")

    for field, value in updates.items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student


def delete_student(db: Session, student_id: int) -> dict:
    student = get_student(db, student_id)
    active = [ib for ib in student.issued_books if ib.status.value == "issued"]
    if active:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete student with active issued books",
        )
    db.delete(student)
    db.commit()
    return {"detail": "Student deleted"}
