from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, EmailStr

'''Блок моделей для валидации данных'''

class User(BaseModel):
    username: str
    email: EmailStr
    password: str

class SchemaUser(User):
    id: int

class Author(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[date] = None

class SchemaAuthor(Author):
    id: int
    model_config = ConfigDict(from_attributes=True)


class Book(BaseModel):
    title: str
    author: Optional[Author]
    description: Optional[str] = None
    available_copies: int = Field(default=1)

class SchemaBook(Book):
    id: int
    model_config = ConfigDict(from_attributes=True)


class Borrow(BaseModel):
    book_id: int
    borrower_name: str
    borrow_date: date

class SchemaBarrow(Borrow):
    id: int
    return_date: Optional[date] = None
    model_config = ConfigDict(from_attributes=True)
