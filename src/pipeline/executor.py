
from sqlalchemy import text
from sqlalchemy.engine import Engine


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
        print("[DRY RUN] Transactional execution")

        with engine.connect() as connection:
            transaction = connection.begin()

            try:
                result = connection.execute(
                    text(sql), params
                )

                # Capture useful information before rollback
                rowcount = result.rowcount

            finally:
                transaction.rollback()

        print("[DRY RUN] Transaction rolled back")
        return rowcount

    with engine.begin() as connection:
        result = connection.execute(
            text(sql), params
        )

        return result.rowcount
