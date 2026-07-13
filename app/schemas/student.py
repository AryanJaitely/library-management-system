from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class StudentBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    enrollment_no: str
    address: Optional[str] = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class StudentOut(StudentBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
