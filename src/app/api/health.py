"""Read-only liveness and readiness checks for the optional REST API."""

import logging
import os
from datetime import datetime, timezone

from fastapi.responses import JSONResponse
from sqlalchemy import text

from src.pipeline.database import create_db_engine
from src.pipeline.reader import read_sql


logger = logging.getLogger(__name__)
SERVICE = "Global Superstore DSS API"


def live() -> dict:
    """Process-only check: no external dependencies are queried."""
    return {"status": "ok", "service": SERVICE}


def _readiness_payload() -> tuple[dict, int]:
    checked_at = datetime.now(timezone.utc).isoformat()
    base_name = os.getenv("DB_NAME")
    payload = {
        "status": "ok",
        "service": SERVICE,
        "checked_at": checked_at,
        "database": base_name,
        "session": "unknown",
        "checks": {
            "control_database": "skipped",
            "active_database": "skipped",
            "gold": "skipped",
        },
    }
    if not base_name:
        payload["status"] = "unavailable"
        payload["checks"]["control_database"] = "not_configured"
        return payload, 503

    stage = "control_database"
    engine = None
    try:
        engine = create_db_engine(database=base_name, connect_timeout=3)
        with engine.begin() as conn:
            conn.execute(text(read_sql("api/health_timeout.sql")))
            conn.execute(text(read_sql("system/ping.sql"))).scalar_one()
            session_table = conn.execute(text(read_sql("api/health_session_table.sql"))).scalar_one()
            if session_table is None:
                selected_name = None
            else:
                selected_name = conn.execute(
                    text(read_sql("api/health_active_database.sql"))
                ).scalar_one_or_none()
            active_name = selected_name or base_name
        payload["checks"]["control_database"] = "ok"
        payload["database"] = active_name
        payload["session"] = "uploaded" if selected_name else "base"
    except Exception as exc:
        logger.warning("Readiness check failed at %s: %s", stage, type(exc).__name__)
        payload["status"] = "unavailable"
        payload["checks"][stage] = "failed"
        return payload, 503
    finally:
        if engine is not None:
            engine.dispose()

    stage = "active_database"
    engine = None
    try:
        engine = create_db_engine(database=active_name, connect_timeout=3)
        with engine.begin() as conn:
            conn.execute(text(read_sql("api/health_timeout.sql")))
            conn.execute(text(read_sql("system/ping.sql"))).scalar_one()
            payload["checks"]["active_database"] = "ok"
            stage = "gold"
            relations = conn.execute(text(read_sql("api/health_gold_tables.sql"))).mappings().all()
            missing = [row["table_name"] for row in relations if not row["present"]]
            if missing:
                payload["missing_gold_tables"] = missing
                raise ValueError("Required Gold tables are missing")
            has_sales = conn.execute(text(read_sql("api/health_gold_rows.sql"))).scalar_one()
            if not has_sales:
                raise ValueError("Gold has no sales")
            payload["checks"]["gold"] = "ok"
    except Exception as exc:
        logger.warning("Readiness check failed at %s: %s", stage, type(exc).__name__)
        payload["status"] = "unavailable"
        payload["checks"][stage] = "failed"
        return payload, 503
    finally:
        if engine is not None:
            engine.dispose()
    return payload, 200


def ready() -> JSONResponse:
    """Check the currently selected UI database without changing its state."""
    payload, status_code = _readiness_payload()
    return JSONResponse(content=payload, status_code=status_code)
