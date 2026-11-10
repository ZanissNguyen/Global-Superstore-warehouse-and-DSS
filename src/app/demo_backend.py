"""Isolated 500-row upload demo. The configured database is never altered by ETL."""

import hashlib
import io
import json
import os
import subprocess
import uuid

import pandas as pd
from sqlalchemy import text

from src.etl.bronze.extract import REQUIRED_COLUMNS
from src.etl.bronze.data_to_bronze import main as run_bronze
from src.etl.silver.transform import main as run_silver
from src.etl.gold.load_dimensions import main as run_dimensions
from src.etl.gold.load_facts import main as run_facts
from src.pipeline.database import create_db_engine, database_scope
from src.pipeline.flows.refresh_warehouse import refresh_all_marts
from src.etl.incremental.demo_incremental import get_warehouse_metrics
from src.dss.predictive.run import run_forecasts
from src.dss.association.run import extract_baskets, mine_association_rules, persist_rules


def base_database():
    return os.environ["DB_NAME"]


def _control_tables(engine):
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS public.demo_session (
                session_id TEXT PRIMARY KEY,
                database_name TEXT NOT NULL,
                source_hash TEXT NOT NULL,
                ingestion_id INTEGER,
                forecast_3_id INTEGER,
                forecast_6_id INTEGER,
                association_run_id INTEGER,
                activated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN NOT NULL DEFAULT FALSE
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS public.demo_job (
                job_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                step TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text("""
            ALTER TABLE public.demo_session
                ADD COLUMN IF NOT EXISTS metrics_before JSONB;
            ALTER TABLE public.demo_session
                ADD COLUMN IF NOT EXISTS metrics_after JSONB;
        """))


def active_session():
    engine = create_db_engine(database=base_database())
    try:
        _control_tables(engine)
        with engine.connect() as conn:
            row = conn.execute(text("""
                SELECT session_id, database_name, ingestion_id, forecast_3_id,
                       forecast_6_id, association_run_id, activated_at,
                       metrics_before, metrics_after
                FROM public.demo_session WHERE active ORDER BY activated_at DESC LIMIT 1
            """)).mappings().first()
        return dict(row) if row else None
    finally:
        engine.dispose()


def active_database():
    session = active_session()
    return session["database_name"] if session else base_database()


def return_to_base(session_id: str) -> None:
    """Deactivate the selected demo session without deleting either database."""
    engine = create_db_engine(database=base_database())
    try:
        _control_tables(engine)
        with engine.begin() as conn:
            changed = conn.execute(text("""
                UPDATE public.demo_session
                SET active = FALSE
                WHERE session_id = :session_id AND active = TRUE
                RETURNING session_id
            """), {"session_id": session_id}).scalar_one_or_none()
            if changed is None:
                raise ValueError("Phiên hoạt động đã thay đổi; hãy tải lại trang.")
    finally:
        engine.dispose()


def history():
    engine = create_db_engine(database=base_database())
    try:
        _control_tables(engine)
        return pd.read_sql(text("""
            SELECT s.session_id, s.activated_at, s.ingestion_id, s.active,
                   s.forecast_3_id, s.forecast_6_id, s.association_run_id
            FROM public.demo_session s ORDER BY s.activated_at DESC LIMIT 10
        """), engine)
    finally:
        engine.dispose()


def _read_csv(content):
    last_error = None
    for encoding in ("utf-8-sig", "cp1252", "latin1"):
        try:
            return pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False, encoding=encoding)
        except (UnicodeError, pd.errors.ParserError) as exc:
            last_error = exc
    raise ValueError(f"Không đọc được CSV: {last_error}")


def validate_upload(content):
    df = _read_csv(content)
    missing = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"Thiếu cột: {', '.join(missing)}")
    if len(df) != 500:
        raise ValueError(f"File demo phải có 500 dòng; hiện có {len(df)}.")
    row_ids = pd.to_numeric(df["Row ID"].str.strip(), errors="coerce")
    if row_ids.isna().any() or row_ids.duplicated().any():
        raise ValueError("Row ID phải là số nguyên duy nhất trong file.")
    if (row_ids % 1 != 0).any():
        raise ValueError("Row ID phải là số nguyên.")
    if df[REQUIRED_COLUMNS].apply(lambda col: col.str.strip().eq("")).any().any():
        raise ValueError("Có ô trống ở cột bắt buộc.")
    for column in ("Sales", "Profit", "Quantity", "Discount"):
        if pd.to_numeric(df[column], errors="coerce").isna().any():
            raise ValueError(f"Cột {column} chứa giá trị không phải số.")
    for column in ("Order Date", "Ship Date"):
        parsed = pd.to_datetime(df[column], dayfirst=True, errors="coerce")
        if parsed.isna().any():
            raise ValueError(f"Cột {column} có ngày không hợp lệ.")
    engine = create_db_engine(database=base_database())
    try:
        with engine.connect() as conn:
            collisions = conn.execute(text("""
                SELECT COUNT(*) FROM silver.orders WHERE row_id = ANY(:ids)
            """), {"ids": row_ids.astype(int).tolist()}).scalar_one()
        if collisions:
            raise ValueError(f"{collisions} Row ID đã tồn tại trong dữ liệu nền.")
    finally:
        engine.dispose()
    dates = pd.to_datetime(df["Order Date"], dayfirst=True)
    return df, {
        "rows": len(df), "orders": df["Order ID"].nunique(),
        "first_date": dates.min().date(), "last_date": dates.max().date(),
        "sales": float(pd.to_numeric(df["Sales"]).sum()),
        "profit": float(pd.to_numeric(df["Profit"]).sum()),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def _docker(*args):
    process = subprocess.run(
        ["docker", "exec", "-e", "PGPASSWORD", "superstore_postgres", *args],
        env={**os.environ, "PGPASSWORD": os.environ["DB_PASSWORD"]},
        capture_output=True, text=True, timeout=300,
    )
    if process.returncode:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip())


def _clone_database(candidate):
    base = base_database()
    if not candidate.startswith("demo_") or not candidate[5:].isalnum():
        raise ValueError("Tên database ứng viên không hợp lệ.")
    control = create_db_engine(database=base)
    dump_path = f"/tmp/{candidate}.dump"
    try:
        _docker("pg_dump", "-h", "localhost", "-U", os.environ["DB_USER"],
                "-d", base, "-Fc", "-f", dump_path)
        with control.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(text(f'CREATE DATABASE "{candidate}"'))
        _docker("pg_restore", "-h", "localhost", "-U", os.environ["DB_USER"],
                "-d", candidate, "--no-owner", "--no-privileges", dump_path)
    finally:
        try:
            _docker("rm", "-f", dump_path)
        finally:
            control.dispose()


def _job(engine, job_id, session_id, step, status, message=""):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO public.demo_job(job_id, session_id, step, status, message)
            VALUES (:job, :session, :step, :status, :message)
            ON CONFLICT(job_id) DO UPDATE SET step = EXCLUDED.step,
                status = EXCLUDED.status, message = EXCLUDED.message,
                updated_at = CURRENT_TIMESTAMP
        """), {"job": job_id, "session": session_id, "step": step,
                "status": status, "message": message[:1000]})


def process_upload(content, filename, progress):
    """Return before/after metrics; activate candidate only after every stage succeeds."""
    session_id = uuid.uuid4().hex[:12]
    candidate = f"demo_{session_id}"
    job_id = uuid.uuid4().hex[:12]
    control = create_db_engine(database=base_database())
    _control_tables(control)
    current_step = "Kiểm tra file"
    try:
        _job(control, job_id, session_id, current_step, "running")
        progress(current_step, "running")
        df, preview = validate_upload(content)
        _job(control, job_id, session_id, current_step, "success")
        progress(current_step, "success")
        base_engine = create_db_engine(database=base_database())
        try:
            before = get_warehouse_metrics(base_engine)
        finally:
            base_engine.dispose()
        current_step = "Tạo database demo"
        _job(control, job_id, session_id, current_step, "running")
        progress(current_step, "running")
        _clone_database(candidate)
        _job(control, job_id, session_id, current_step, "success")
        progress(current_step, "success")
        candidate_engine = create_db_engine(database=candidate)
        with database_scope(candidate):
            # Upload bytes are staged in memory until this button is pressed.
            from tempfile import TemporaryDirectory
            from pathlib import Path
            with TemporaryDirectory() as folder:
                safe_name = Path(filename).name
                if not safe_name.lower().endswith(".csv"):
                    raise ValueError("Chỉ hỗ trợ file CSV.")
                staged = Path(folder) / safe_name
                staged.write_bytes(content)
                for label, operation in (
                    ("Bronze", lambda: run_bronze(input_path=staged)),
                    ("Silver", run_silver),
                    ("Gold", lambda: (run_dimensions(), run_facts())),
                ):
                    current_step = label
                    _job(control, job_id, session_id, label, "running")
                    progress(label, "running")
                    operation()
                    _job(control, job_id, session_id, label, "success")
                    progress(label, "success")
            current_step = "Đối soát"
            _job(control, job_id, session_id, current_step, "running")
            progress(current_step, "running")
            after = get_warehouse_metrics(candidate_engine)
            for key in ("bronze_rows", "silver_rows", "gold_rows"):
                if after[key] - before[key] != len(df):
                    raise ValueError(f"{key} tăng {after[key] - before[key]}, kỳ vọng {len(df)}.")
            for key in ("total_sales", "total_profit"):
                expected = preview["sales" if key == "total_sales" else "profit"]
                if abs(float(after[key] - before[key]) - expected) > 0.02:
                    raise ValueError(f"{key} không khớp file CSV.")
            _job(control, job_id, session_id, current_step, "success")
            progress(current_step, "success")
            current_step = "Refresh marts"
            _job(control, job_id, session_id, current_step, "running")
            progress(current_step, "running")
            refresh_all_marts()
            _job(control, job_id, session_id, current_step, "success")
            progress(current_step, "success")
            current_step = "Dự báo và bán kèm"
            _job(control, job_id, session_id, current_step, "running")
            progress(current_step, "running")
            forecasts = run_forecasts(candidate_engine)
            baskets = extract_baskets(candidate_engine)
            tx, rules = mine_association_rules(baskets)
            rule_id = persist_rules(candidate_engine, tx, rules, 0.0001, 0.10, 1.2)
            _job(control, job_id, session_id, current_step, "success")
            progress(current_step, "success")
        candidate_engine.dispose()
        current_step = "Kích hoạt phiên"
        _job(control, job_id, session_id, current_step, "running")
        progress(current_step, "running")
        with control.begin() as conn:
            conn.execute(text("UPDATE public.demo_session SET active = FALSE WHERE active"))
            conn.execute(text("""
                INSERT INTO public.demo_session
                    (session_id, database_name, source_hash, ingestion_id,
                     forecast_3_id, forecast_6_id, association_run_id,
                     metrics_before, metrics_after, active)
                VALUES (:session, :database, :hash, :ingestion, :f3, :f6, :rule,
                        CAST(:before AS JSONB), CAST(:after AS JSONB), TRUE)
            """), {"session": session_id, "database": candidate,
                    "hash": preview["sha256"], "ingestion": after["latest_ingestion_id"],
                    "f3": forecasts[3], "f6": forecasts[6], "rule": rule_id,
                    "before": json.dumps(before, default=str),
                    "after": json.dumps(after, default=str)})
        _job(control, job_id, session_id, current_step, "success")
        progress(current_step, "success")
        return {"session_id": session_id, "job_id": job_id,
                "before": before, "after": after, "preview": preview}
    except Exception as exc:
        _job(control, job_id, session_id, current_step, "error", str(exc))
        progress(current_step, "error")
        raise
    finally:
        control.dispose()
