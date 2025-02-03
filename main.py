from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.DB.database import create_tables, delete_tables, get_db
from src.pydentic_models.models import Author, Book, Borrow, SchemaAuthor, SchemaBook, SchemaBarrow
from src.repository.repository import AuthorRepository, BookRepository, BorrowRepository



@asynccontextmanager
async def lifespan(app: FastAPI):
   await create_tables()
   print("База готова")
   yield
   await delete_tables()
   print("База очищена")

app = FastAPI(lifespan=lifespan)


# Эндпоинтs для авторов
@app.post("/", response_model=SchemaAuthor)  # Предполагаю, что это ваша схема для возвращаемого автора
async def create_author(data: Author, db: AsyncSession = Depends(get_db)):
    return await AuthorRepository.create_author(data, db)

@app.get("/authors", response_model=List[SchemaAuthor])
async def get_all_authors(db: AsyncSession = Depends(get_db)):
    return await AuthorRepository.get_authors(db)

@app.get("/authors/{id}", response_model=SchemaAuthor)  # Добавлен новый метод для получения автора по ID
async def get_author_by_id(id: int, db: AsyncSession = Depends(get_db)):
    author = await AuthorRepository.get_author_by_id(id, db)
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return author

@app.patch("/authors/{id}", response_model=SchemaAuthor)
async def update_author(author_id: int, author_data: Author, db: AsyncSession = Depends(get_db)):
    updated_author = await AuthorRepository.update_author(author_data.model_dump(), db)
    if updated_author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return updated_author

@app.delete("/authors/{id}", response_model=SchemaAuthor)
async def delete_author(id: int, db: AsyncSession = Depends(get_db)):
    deleted_author = await AuthorRepository.delete_author(id, db)
    if deleted_author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return deleted_author


# Эндпоинты для книг

@app.post("/books", response_model=SchemaBook)
async def create_book(book_data: Book, db: AsyncSession = Depends(get_db)):
    book_repository = BookRepository()

    created_book = await book_repository.create_book(book_data, db)

    if not created_book:
        raise HTTPException(status_code=400, detail="Не удалось создать книгу")
    return created_book


@app.get("/books", response_model=List[SchemaBook])
async def get_books(db: AsyncSession = Depends(get_db)):
    books = await BookRepository.get_books(db)
    return books

@app.get("/books/{id}")
async def get_book_by_id(book_id: int, db: AsyncSession = Depends(get_db)):
    book = await BookRepository.get_book_by_id(book_id, db)
    if book:
        return book
    raise HTTPException(status_code=404, detail="Книга не найдена")

@app.patch("/books/{book_id}", response_model=SchemaBook)
async def update_book(book_id: int, book_data: Book, db: AsyncSession = Depends(get_db)):
    book = Book.model_dump(book_data)
    updated_book = await BookRepository.update_book(book_id, book, db)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return updated_book

@app.delete("/books/{id}", response_model=SchemaBook)
async def delete_book(id: int, db: AsyncSession = Depends(get_db)):
    deleted_book = await BookRepository.delete_book(id, db)
    if deleted_book:
        return deleted_book
    raise HTTPException(status_code=404, detail="Книга не найдена")

# Эндпоинты для выдач

@app.post("/borrows", response_model=Borrow)
async def create_borrow(borrow: Borrow, db: AsyncSession = Depends(get_db)):
    new_borrow = await BorrowRepository.create_borrow(borrow.model_dump(), db)
    return new_borrow

@app.get("/borrows", response_model=List[Borrow])
async def get_borrows(db: AsyncSession = Depends(get_db)):
    borrows = await BorrowRepository.get_borrows(db)
    return borrows

@app.get("/borrows/{id}", response_model=Borrow)
async def get_borrow_by_id(id: int, db: AsyncSession = Depends(get_db)):
    borrow = await BorrowRepository.get_borrow_by_id(id, db)
    if borrow:
        return borrow
    raise HTTPException(status_code=404, detail="Выдача не найдена")

@app.patch("/borrows/{id}/return", response_model=SchemaBarrow)
async def return_borrow(id: int, return_date: str, db: AsyncSession = Depends(get_db)):
    returned_borrow = await BorrowRepository.return_borrow(id, return_date, db)
    if returned_borrow:
        return returned_borrow
    raise HTTPException(status_code=404, detail="Выдача не найдена")
