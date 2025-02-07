import jwt

from datetime import timedelta, datetime, timezone, date
from typing import List, Optional, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.config import settings
from src.models.orm_models import AuthorOrm, BookOrm, BorrowOrm, UserOrm
from src.models.pydentic_models import Author, Book, SchemaBook, SchemaAuthor, User

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

'''Блок функциональных методов класса User для регистрации и авторизации'''


class UserRepository:
    @staticmethod
    async def create_user(user: User, db: AsyncSession):
        hashed_password = pwd_context.hash(user.password)
        db_user = UserOrm(username=user.username, email=user.email, password=hashed_password)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def get_user_by_username(username: str, db: AsyncSession):
        result = await db.execute(select(UserOrm).where(UserOrm.username == username))
        return result.scalars().first()

    @staticmethod
    async def get_all_user_emails(db: AsyncSession):
        result = await db.execute(select(User.email))
        return [row[0] for row in result.scalars().all()]

'''Блок функциональных методов CRUD'''

class AuthorRepository:
    @classmethod
    async def create_author(cls, data: Author, db: AsyncSession) -> AuthorOrm:
        model = data.model_dump()
        existing_author = await cls.get_author_by_details(model, db)

        if existing_author:
            return existing_author
        else:
            new_model = AuthorOrm(**model)
            db.add(new_model)
            await db.flush()  # Используем flush для получения ID
            await db.commit()
            return new_model

    @classmethod
    async def get_author_by_details(cls, data: dict, db: AsyncSession) -> Optional[AuthorOrm]:
        result = await db.execute(select(AuthorOrm).filter(
            (data['first_name'] == AuthorOrm.first_name) &
            (data['last_name'] == AuthorOrm.last_name) &
            (data['birth_date'] == AuthorOrm.birth_date)
        ))
        author = result.scalars().first()
        return author

    @classmethod
    async def get_authors(cls, db: AsyncSession) -> List[AuthorOrm]:
        query = select(AuthorOrm)
        result = await db.execute(query)
        authors = result.scalars().all()
        return authors if authors else []

    @classmethod
    async def get_author_by_id(cls, author_id: int, db: AsyncSession) -> Optional[AuthorOrm]:
        author = await db.get(AuthorOrm, author_id)
        return author if author else None

    @classmethod
    async def update_author(cls, id: int, author_data: dict, db: AsyncSession) -> Type[AuthorOrm] | None:
        stored_author = await db.get(AuthorOrm, id)
        if stored_author:
            for key, value in author_data.items():
                setattr(stored_author, key, value)
            await db.commit()
            return stored_author
        return None

    @classmethod
    async def delete_author(cls, id: int, db: AsyncSession) -> Optional[AuthorOrm]:
        author_to_delete = await db.get(AuthorOrm, id)
        if author_to_delete:
            await db.delete(author_to_delete)
            await db.commit()
            return author_to_delete
        return None

class BookRepository:
    @classmethod
    async def create_book(cls, book_data: Book, db: AsyncSession):
        data = book_data.model_dump()
        author_data = data['author']
        available_copies = data.get('available_copies', 1)

        existing_author = await cls.get_existing_author(author_data, db)

        if existing_author:
            author_id = existing_author.id
        else:
            new_author = AuthorOrm(**author_data)
            db.add(new_author)
            await db.flush()
            author_id = new_author.id

        query = await db.execute(
            select(BookOrm).filter(BookOrm.title == data['title'], BookOrm.author_id == author_id)
        )
        existing_book = query.scalars().first()

        if existing_book:
            existing_book.available_copies += 1
            await db.commit()
            return existing_book.model_dump()
        else:
            new_book_data = data.copy()
            new_book_data['available_copies'] = available_copies
            new_book = BookOrm(
                title=new_book_data['title'],
                description=new_book_data['description'],
                available_copies=new_book_data['available_copies'],
                author_id=author_id
            )

            db.add(new_book)
            await db.flush()
            await db.commit()

            return new_book.model_dump()

    @classmethod
    async def get_existing_author(cls, author_data: dict, db: AsyncSession) -> Optional[AuthorOrm]:
        author = await AuthorRepository.get_author_by_details(author_data, db)
        return author

    @classmethod
    async def get_books(cls, db: AsyncSession) -> List[SchemaBook]:
        query = select(BookOrm).options(joinedload(BookOrm.author))
        result = await db.execute(query)
        books = result.scalars().all()

        schema_books = []
        for book in books:
            author_data = None
            if book.author:
                author_data = {
                    'id': book.author.id,
                    'first_name': book.author.first_name,
                    'last_name': book.author.last_name,
                    'birth_date': book.author.birth_date.strftime('%Y-%m-%d') if book.author.birth_date else None
                }

            schema_books.append(SchemaBook(
                id=book.id,
                title=book.title,
                description=book.description,
                available_copies=book.available_copies,
                author=SchemaAuthor(**author_data) if author_data else None
            ))

        return schema_books

    @classmethod
    async def get_book_by_id(cls, book_id: int, db: AsyncSession) -> Optional[SchemaBook]:
        query = select(BookOrm).where(BookOrm.id == book_id).options(joinedload(BookOrm.author))
        book_orm = await db.execute(query)
        book = book_orm.scalars().first()

        if book:
            author_data = None
            if book.author:
                author_data = {
                    'id': book.author.id,
                    'first_name': book.author.first_name,
                    'last_name': book.author.last_name,
                    'birth_date': book.author.birth_date.strftime('%Y-%m-%d') if book.author.birth_date else None
                }

            return SchemaBook(
                id=book.id,
                title=book.title,
                description=book.description,
                available_copies=book.available_copies,
                author=SchemaAuthor(**author_data) if author_data else None
            )
        else:
            return None

    @classmethod
    async def update_book(cls, book_id: int, book_data: dict, db: AsyncSession) -> Type[BookOrm] | None:
        stored_book = await db.get(BookOrm, book_id)
        if stored_book:
            for key, value in book_data.items():
                if key not in ['author', 'available_copies']:
                    setattr(stored_book, key, value)

            if 'author' in book_data:
                author_data = book_data['author']
                if author_data:
                    existing_author = await db.get(AuthorOrm, author_data.get('id'))
                    if existing_author:

                        for attr, attr_value in author_data.items():
                            setattr(existing_author, attr, attr_value)
                    else:
                        new_author = AuthorOrm(**author_data)
                        db.add(new_author)
                        stored_book.author = new_author

            if 'available_copies' in book_data:
                stored_book.available_copies = book_data['available_copies']

            await db.commit()
            return stored_book

        return None

    @classmethod
    async def delete_book(cls, id: int, db: AsyncSession) -> Type[BookOrm] | None:
        book_to_delete = await db.get(BookOrm, id)
        if book_to_delete:
            await db.delete(book_to_delete)
            await db.commit()
            return book_to_delete
        return None

    @classmethod
    async def borrow_book(cls, book_id: int, db: AsyncSession) -> bool:
        book = await db.get(BookOrm, book_id)
        if book:
            if book.available_copies > 0:
                book.available_copies -= 1
                await db.commit()
                return True
            else:
                raise ValueError("Все копии книги 'на руках'.")
        else:
            raise ValueError("Книга не найдена.")

    @classmethod
    async def return_book(cls, book_id: int, db: AsyncSession) -> Type[BookOrm] | None:
        book = await db.get(BookOrm, book_id)
        if book:
            book.available_copies += 1
            await db.commit()
            return book
        return None


class BorrowRepository:
    @classmethod
    async def create_borrow(cls, borrow_data: dict, db: AsyncSession) -> BorrowOrm:
        borrower_name = borrow_data.get("borrower_name")
        book_id = borrow_data.get("book_id")
        borrow_date = borrow_data.get("borrow_date")

        if not borrower_name or not book_id or not borrow_date:
            raise ValueError("Не все обязательные поля были предоставлены для создания borrow_data")

        # Проверяем тип borrow_date
        if isinstance(borrow_date, str):
            try:
                # Преобразуем строку в объект date
                borrow_date = datetime.strptime(borrow_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError("Неверный формат даты. Ожидается формат YYYY-MM-DD.")
        elif not isinstance(borrow_date, (datetime, date)):
            raise ValueError("borrow_date должен быть строкой или объектом datetime.")

        new_borrow = BorrowOrm(
            borrower_name=borrower_name,
            book_id=book_id,
            borrow_date=borrow_date
        )
        db.add(new_borrow)
        await BookRepository.borrow_book(book_id, db)
        await db.commit()
        return new_borrow

    @classmethod
    async def get_borrows(cls, db: AsyncSession) -> List[BorrowOrm]:
        query = select(BorrowOrm)
        result = await db.execute(query)
        borrows = result.scalars().all()
        return borrows

    @classmethod
    async def get_borrow_by_id(cls, id: int, db: AsyncSession) -> Optional[BorrowOrm]:
        borrow = await db.get(BorrowOrm, id)
        return borrow

    @classmethod
    async def return_borrow(cls, borrow_id: int, return_date_str: str, db: AsyncSession) -> Optional[BorrowOrm]:
        # Получаем запись о займе
        borrow_to_return = await db.get(BorrowOrm, borrow_id)
        if borrow_to_return:
            # Преобразуем строку в объект date
            try:
                return_date = datetime.strptime(return_date_str, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError("Неверный формат даты. Ожидается формат YYYY-MM-DD.")

            # Устанавливаем дату возврата
            borrow_to_return.return_date = return_date

            # Возвращаем книгу
            await BookRepository.return_book(borrow_to_return.book_id, db)

            await db.commit()  # Сохраняем изменения
            return borrow_to_return

        return None

