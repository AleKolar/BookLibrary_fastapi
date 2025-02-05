import asyncio
import sys
import pathlib
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from src.DB.database import Model
from src.config.config import settings

# Определите целевую метадату для миграций
target_metadata = Model.metadata

# Добавьте родительский каталог текущего файла в sys.path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

# Функция для выполнения миграций
def do_run_migrations(connection):
    context.configure(
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
        version_table_schema=target_metadata.schema,
    )

    with context.begin_transaction():
        context.run_migrations()

# Асинхронная функция для выполнения миграций онлайн
async def run_migrations_online():
    """Выполнить миграции в 'онлайн' режиме."""
    # Создайте асинхронный движок базы данных с использованием URI из настроек
    connectable = create_async_engine(settings.ASYNC_DATABASE_URI, future=True)

    # Подключитесь к базе данных и выполните миграции в транзакции
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

# Запустите миграции онлайн с использованием asyncio
if __name__ == "__main__":
    asyncio.run(run_migrations_online())


