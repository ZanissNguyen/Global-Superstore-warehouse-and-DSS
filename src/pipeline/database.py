
import os

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def create_db_engine() -> Engine:
    """
    Create SQLAlchemy engine with connection pooling.
    """

    connection_url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME"),
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
