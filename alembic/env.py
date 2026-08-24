import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Pull in the app's Base and every model module so target_metadata is
# fully populated - same set main.py imports, kept in one place here so
# autogenerate always sees the complete schema.
from app.database import Base, DATABASE_URL
from app.models.org import Org  # noqa: F401
from app.models.identity import Person, RoleAssignment  # noqa: F401
from app.models.admission import AdmissionApplication  # noqa: F401
from app.models.asset import Asset  # noqa: F401
from app.models.staff import JobApplication  # noqa: F401
from app.models.academic import (  # noqa: F401
    Term, Course, SubjectRequirementTemplate,
    SectionPlan, ResourcePlanRun, ResourcePlanAssignment, ResourceGap,
    SchoolClass, ClassEnrollment, CourseSection, Topic, CalendarDay,
    ClassSession, ClassSessionLog, AttendanceRecord, Assessment, Score,
)
from app.models.notification import Notification  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode - emits SQL to script output
    instead of executing against a live DB."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode against the real (async) DB."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={"statement_cache_size": 0},
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
