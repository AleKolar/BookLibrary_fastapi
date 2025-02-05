from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column,DeclarativeBase


'''Блок моделей для базы данных'''

class Model(DeclarativeBase):
   pass


class AuthorOrm(Model):
    __tablename__ = 'author'
    id: Mapped[int | None] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    birth_date: Mapped[datetime | None]

    book: Mapped["BookOrm"] = relationship("BookOrm", back_populates="author", lazy='joined')


    def model_dump(self):
        return {
        'id': self.id,
        'first_name': self.first_name,
        'last_name': self.last_name,
        'birth_date': self.birth_date.strftime('%Y-%m-%d') if self.birth_date else None
        }

class BookOrm(Model):
    __tablename__ = 'book'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str | None]
    available_copies: Mapped[int]
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey('author.id'), nullable=True)

    borrows: Mapped["Borrow"] = relationship("BorrowOrm", back_populates="book", foreign_keys="[BorrowOrm.book_id]", lazy='joined')
    author: Mapped[Optional["Author"]] = relationship("AuthorOrm", back_populates="book", lazy='joined')

    def model_dump(self):
        return {
        'id': self.id,
        'title': self.title,
        'description': self.description,
        'author': self.author.model_dump() if self.author else None,  # Use the full author object
        'available_copies': self.available_copies,
        }


class BorrowOrm(Model):
    __tablename__ = 'borrow'
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey('book.id'))
    borrower_name: Mapped[str]
    borrow_date: Mapped[datetime | None]
    return_date: Mapped[datetime | None]

    book: Mapped["BookOrm"] = relationship("BookOrm", back_populates="borrows", lazy='joined')


    def model_dump(self):
        return {
            'book_id': self.book_id,
            'borrower_name': self.borrower_name,
            'borrow_date': self.borrow_date,
        }
