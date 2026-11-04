"""
OLAP Test Suite Runner
Executes all core OLAP analytical queries (Roll-up, Drill-down, Slice, Dice, Pivot, Window, Cube)
and displays formatted execution results and timing.
"""

import time
from src.pipeline.database import create_db_engine
from src.pipeline.executor import query_sql
from src.pipeline.reader import read_sql

OLAP_QUERIES = [
    ("1. ROLL-UP (Time & Geography)", "gold/marts/olap_rollup.sql"),
    ("2. DRILL-DOWN (Category -> Sub-Category -> SKU)", "gold/marts/olap_drilldown.sql"),
    ("3. SLICE & DICE (APAC / EU Subcube)", "gold/marts/olap_slice_dice.sql"),
    ("4. PIVOT (Cross-tabulation by Quarter)", "gold/marts/olap_pivot.sql"),
    ("5. WINDOW FUNCTION (MoM Sales Growth)", "gold/marts/olap_growth_mom.sql"),
    ("6. WINDOW FUNCTION (Top 5 Products per Category)", "gold/marts/olap_top_products.sql"),
    ("7. GROUP BY CUBE (Multi-dimensional Subtotals)", "gold/marts/olap_cube.sql"),
]

def run_suite():
    engine = create_db_engine()
    print("=" * 70)
    print("RUNNING OLAP ANALYTICAL QUERY SUITE")
    print("=" * 70)

    for title, sql_path in OLAP_QUERIES:
        print(f"\n>>> EXECUTING: {title} ({sql_path})")
        t0 = time.time()
        try:
            sql = read_sql(sql_path)
            # if multiple statements, take the first or run
            statements = [s.strip() for s in sql.split(';') if s.strip()]
            for i, stmt in enumerate(statements):
                if len(statements) > 1:
                    print(f"--- Sub-query {i+1} ---")
                df = query_sql(engine, stmt)
                elapsed = (time.time() - t0) * 1000
                print(f"Returned {len(df)} rows in {elapsed:.2f} ms")
                print(df.head(6))
        except Exception as e:
            print(f"Error executing {sql_path}: {e}")

    print("\n" + "=" * 70)
    print("OLAP SUITE EXECUTION COMPLETED")
    print("=" * 70)

if __name__ == "__main__":
    run_suite()
