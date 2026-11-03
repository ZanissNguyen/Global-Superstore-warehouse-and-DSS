import json

from src.pipeline.reader import read_sql

from src.pipeline.executor import execute_sql, insert_dataframe, insert_on_conflict_nothing

def record_ingestion(engine, source_name: str, content_hash: str, loaded_time: str, metadata: dict, dry_run: bool = False, rollback: bool = False):
    return execute_sql(
        engine,
        read_sql("bronze/insert_ingestion.sql"),
        {
            "source_name": source_name,
            "content_hash": content_hash,
            "loaded_time": loaded_time,
            "metadata": json.dumps(metadata)
        },
        dry_run,
        rollback
    )['return'][0]['id']

def record_market(engine, ingestion_id, unique_market, market_count: int, dry_run: bool = False, rollback: bool = False):
    if market_count == 0:
        pass

    to_write = unique_market.copy()
    to_write["ingestion"] = ingestion_id
    return insert_dataframe(
        df=to_write,
        engine=engine,
        table_name="market",
        schema_name="bronze",
        exist_mode="append",
        chunk_size = 50,
        execute_method=insert_on_conflict_nothing(["Country", "Market"]),
        dry_run=dry_run,
        rollback=rollback,
    )

def record_pin(engine, ingestion_id, unique_pin, pin_count: int, dry_run: bool = False, rollback: bool = False):
    if pin_count == 0:
            pass
    
    to_write = unique_pin.copy()
    to_write["ingestion"] = ingestion_id
    return insert_dataframe(
        df=to_write,
        engine=engine,
        table_name="postal_code",
        schema_name="bronze",
        exist_mode="append",
        chunk_size = 100,
        execute_method=insert_on_conflict_nothing(["City", "State", "Country", "Postal Code"]),
        dry_run=dry_run,
        rollback=rollback,
    )

def record_raw_orders(engine, ingestion_id, df, dry_run: bool = False, rollback: bool = False):
    to_write = df.copy()
    to_write["ingestion"] = ingestion_id
    return insert_dataframe(
        df=to_write,
        engine=engine,
        table_name="raw_orders",
        schema_name="bronze",
        exist_mode="append",
        chunk_size = 100,
        # execute_method=insert_on_conflict_nothing(["Row ID"]),
        execute_method="multi",
        dry_run=dry_run,
        rollback=rollback,
    )