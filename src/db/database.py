
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from src.config import settings
from src.models.orm_models import Model

DATABASE_URL = settings.get_db_url()

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

engine = create_async_engine(DATABASE_URL, future=True, echo=True)
new_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False,)

# Генератор для получения сессий
async def get_db():
    async with new_session() as db:
        yield db


async def create_tables():
   async with engine.begin() as conn:
       await conn.run_sync(Model.metadata.create_all)

async def delete_tables():
   async with engine.begin() as conn:
       await conn.run_sync(Model.metadata.drop_all)