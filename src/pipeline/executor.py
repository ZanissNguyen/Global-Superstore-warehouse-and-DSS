
from sqlalchemy import text
from sqlalchemy.engine import Engine
import pandas as pd


def execute_sql(
    engine: Engine,
    sql: str,
    params: dict | None = None,
    dry_run: bool = False,
    rollback: bool = False,
):
    params = params or {}

    if dry_run and not rollback:
        print("[DRY RUN] SQL preview:")
        print(sql)
        print("[DRY RUN] Parameters:", params)
        return None

    if dry_run and rollback:
        with engine.connect() as connection:
            transaction = connection.begin()

            try:
                result = connection.execute(text(sql), params)
                rowcount = result.rowcount
            finally:
                transaction.rollback()

        return {
            "success": True,
            "rowcount": rowcount,
            "rolled_back": True,
        }

    with engine.begin() as connection:
        result = connection.execute(text(sql), params)

        return {
            "success": True,
            "rowcount": result.rowcount,
            "rolled_back": False,
        }

import pandas as pd

def query_sql(
    engine: Engine,
    sql: str,
    params: dict | None = None,
    dry_run: bool = False,
):
    params = params or {}

    if dry_run:
        print("[DRY RUN] SQL preview:")
        print(sql)
        print("[DRY RUN] Parameters:", params)
        return None

    with engine.connect() as connection:
        result = connection.execute(text(sql), params)

        return pd.DataFrame(
            result.fetchall(),
            columns=result.keys()
        )

def truncate_table(
    engine: Engine,
    schema: str,
    table: str,
    dry_run: bool = False,
    rollback: bool = False,
):
    sql = f'TRUNCATE TABLE "{schema}"."{table}" CASCADE;'

    return execute_sql(
        engine,
        sql,
        dry_run=dry_run,
        rollback=rollback,
    )