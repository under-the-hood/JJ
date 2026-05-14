import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.backend.models.base import Base
from app.backend.models.mails import Mails
from app.backend.models.response import Response
from app.backend.models.resume import Resume
from app.backend.models.user import User
from app.backend.models.vacancy import Vacancy
from app.backend.config import settings

config.set_main_option('sqlalchemy.url', f"{settings.database}?async_fallback=True")

cmd_line_url = context.get_x_argument(as_dictionary=True).get("db_url")
if cmd_line_url:
    config.set_main_option("sqlalchemy.url", cmd_line_url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:

    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
