import os
import sys
from logging.config import fileConfig

from alembic import context

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine

import app.models.audit  # noqa: F401
from app.db.session import Base, get_database_url

# Alembic Config object
config = context.config

# Interpret config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    # 1. Direct environment variable (e.g. Render, Heroku, Docker, or CLI)
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        if env_url.startswith("postgres://"):
            env_url = env_url.replace("postgres://", "postgresql://", 1)
        return env_url

    # 2. Config option if explicitly configured and not a placeholder
    cfg_url = config.get_main_option("sqlalchemy.url")
    if cfg_url and "%(DATABASE_URL)s" not in cfg_url and not cfg_url.startswith("driver://"):
        if cfg_url.startswith("postgres://"):
            cfg_url = cfg_url.replace("postgres://", "postgresql://", 1)
        return cfg_url

    # 3. App settings fallback
    return get_database_url()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using target database engine."""
    url = get_url()
    connectable = create_engine(url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
