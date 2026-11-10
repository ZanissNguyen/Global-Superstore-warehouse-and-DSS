
import os
from contextlib import contextmanager
from contextvars import ContextVar

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")
_database_override: ContextVar[str | None] = ContextVar("database_override", default=None)


@contextmanager
def database_scope(database: str):
    """Route existing ETL/DSS functions to an isolated demo database."""
    token = _database_override.set(database)
    try:
        yield
    finally:
        _database_override.reset(token)


def create_db_engine(database: str | None = None) -> Engine:
    """
    Create SQLAlchemy engine with connection pooling.
    """

    connection_url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=database or _database_override.get() or os.getenv("DB_NAME"),
    )

    engine = create_engine(
        connection_url,

        # Connection pool
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,

        # Validate connection before using
        pool_pre_ping=True,

        echo=False,
    )

    return engine


def test_connection(engine: Engine) -> bool:
    """Check whether database is reachable."""

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return True

    except Exception:
        return False
