
from sqlalchemy import text
from sqlalchemy.engine import Engine
import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from src.pipeline.reader import read_sql

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
            "return": result.mappings().all() if result.returns_rows else None,
            "success": True,
            "rowcount": result.rowcount,
            "rolled_back": False,
        }

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
    sql = read_sql("system/truncate_table.sql").format(schema=schema, table=table)

    return execute_sql(
        engine,
        sql,
        dry_run=dry_run,
        rollback=rollback,
    )

# exist_mode = append | replace | fail
# method = multi | None | callable object
def insert_dataframe(
    df: pd.DataFrame,
    engine: Engine,
    table_name: str,
    schema_name: str,
    exist_mode: str = "append",
    chunk_size: int = 1000,
    execute_method: any = None,
    dry_run: bool = False,
    rollback: bool = False,
):
    if dry_run and not rollback:
        print("[DRY RUN] DataFrame insertion preview:")
        print(f"Target: {schema_name}.{table_name}")
        print(f"Rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        print(f"Mode: {exist_mode}")
        print(f"Chunk size: {chunk_size}")
        print(f"Execute method: {execute_method}")

        return None

    with engine.connect() as conn:
        transaction = conn.begin()

        try:
            df.to_sql(
                name=table_name,
                con=conn,
                schema=schema_name,
                if_exists=exist_mode,
                index=False,
                chunksize=chunk_size,
                method=execute_method
            )

            row_count = len(df)

            if dry_run and rollback:
                transaction.rollback()

                return {
                    "success": True,
                    "rowcount": row_count,
                    "rolled_back": True,
                }

            transaction.commit()

            print(
                f"Inserted {row_count} rows "
                f"into {schema_name}.{table_name} successfully."
            )

            return {
                "success": True,
                "rowcount": row_count,
                "rolled_back": False,
            }

        except Exception:
            if transaction.is_active:
                transaction.rollback()
            raise

def insert_on_conflict_nothing(constraints_columns: list[str]):
    def inner(table, conn, keys, data_iter):
        data = [dict(zip(keys, row)) for row in data_iter]

        if not data:
            return 0

        stmt = insert(table.table).values(data)

        stmt = stmt.on_conflict_do_nothing(
            index_elements=constraints_columns
        )

        result = conn.execute(stmt)

        return result.rowcount

    return inner
