from sqlalchemy import Column, Integer, String, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    isbn = Column(String(20), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    total_copies = Column(Integer, nullable=False, default=1)
    available_copies = Column(Integer, nullable=False, default=1)

    author_id = Column(Integer, ForeignKey("authors.id", ondelete="RESTRICT"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)

    __table_args__ = (
        CheckConstraint("total_copies >= 0", name="chk_total_copies_non_negative"),
        CheckConstraint("available_copies >= 0", name="chk_available_copies_non_negative"),
        CheckConstraint("available_copies <= total_copies", name="chk_available_lte_total"),
    )

    author = relationship("Author", back_populates="books")
    category = relationship("Category", back_populates="books")
    issued_books = relationship("IssuedBook", back_populates="book")
