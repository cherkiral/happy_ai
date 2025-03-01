from logging.config import fileConfig

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.config.config import settings

#-----------MODELS IMPORT-----------#
from app.database.models.users import User
from app.database.models.messages import Message
#-----------MODELS IMPORT-----------#

from app.database.database import Base

target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)



def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

from sqlalchemy.ext.asyncio import create_async_engine
import asyncio

def do_run_migrations(connection):
    """Runs the migrations in offline or online mode."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Runs migrations in an asynchronous environment."""
    engine = create_async_engine(settings.DATABASE_URL, future=True, echo=True)

    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()

asyncio.run(run_migrations_online())