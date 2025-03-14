import pathlib
import sys
import asyncio
from logging.config import fileConfig
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from src.DB.orm_models import Model # Импортируйте ваши модели
from src.config.config import settings  # Импортируйте ваши настройки

# Alembic Config object
config = context.config

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Define the target metadata for migrations
target_metadata = Model.metadata

# Add the parent directory of the current file to sys.path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

# Function to run migrations
def do_run_migrations(connection):
    context.configure(
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()

# Asynchronous function to run migrations online
async def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_async_engine(settings.get_db_url(), future=True)

    # Connect to the database and run migrations in a transaction
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

# Run migrations online using asyncio
if __name__ == "__main__":
    asyncio.run(run_migrations_online())


