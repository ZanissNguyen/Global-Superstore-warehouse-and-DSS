"""Run the Gold OLAP examples against the same date and geography scope as the UI.

Use --check-dashboard to reconcile the canonical dashboard aggregates.
"""

import argparse
from datetime import date

from src.pipeline.database import create_db_engine
from src.pipeline.executor import query_sql
from src.pipeline.reader import read_sql


OLAP_QUERIES = (
    ("ROLL-UP", "gold/marts/olap_rollup.sql"),
    ("DRILL-DOWN", "gold/marts/olap_drilldown.sql"),
    ("SLICE / DICE", "gold/marts/olap_slice_dice.sql"),
    ("PIVOT", "gold/marts/olap_pivot.sql"),
    ("MoM GROWTH", "gold/marts/olap_growth_mom.sql"),
    ("TOP PRODUCTS", "gold/marts/olap_top_products.sql"),
    ("CUBE", "gold/marts/olap_cube.sql"),
)


def _date_key(value: date) -> int:
    return int(value.strftime("%Y%m%d"))


def _selected_dates(engine, args):
    bounds = query_sql(engine, read_sql("gold/dashboard/order_date_bounds.sql")).iloc[0]
    first, last = bounds["first_date"], bounds["last_date"]
    if first is None or last is None:
        raise ValueError("Gold has no sales to analyze.")
    first, last = date.fromisoformat(str(first)), date.fromisoformat(str(last))
    start = date.fromisoformat(args.start) if args.start else first
    end = date.fromisoformat(args.end) if args.end else last
    if not first <= start <= end <= last:
        raise ValueError(f"Date range must be within Gold data: {first} to {last}.")
    return start, end


def _params(start, end, args):
    if args.top_n not in range(5, 11):
        raise ValueError("top-n must be between 5 and 10.")
    if args.row_limit < 1:
        raise ValueError("row-limit must be positive.")
    return {
        "start_key": _date_key(start), "end_key": _date_key(end),
        "market": args.market, "region": args.region, "country": args.country,
        "category": args.category, "metric": args.metric,
        "top_n": args.top_n, "row_limit": args.row_limit,
        "year": args.year or end.year,
    }


def _assert_near(actual, expected, label):
    # Dashboard groups round sales/profit to cents; allow accumulated cents.
    tolerance = max(0.5, abs(float(expected)) * 1e-8)
    if abs(float(actual) - float(expected)) > tolerance:
        raise AssertionError(f"{label}: {actual} differs from {expected}")


def check_dashboard(engine, params):
    """Check additive aggregates for the current scope against the UI KPI query."""
    kpi = query_sql(engine, read_sql("gold/dashboard/period_kpis.sql"), params).iloc[0]
    checks = (
        ("category", "gold/dashboard/period_categories.sql"),
        ("trend by month", "gold/dashboard/period_trend.sql"),
        ("market", "gold/dashboard/geo_summary_market.sql"),
        ("customer segment", "gold/dashboard/customer_segments.sql"),
    )
    for label, path in checks:
        query_params = {**params, "grain": "month"}
        grouped = query_sql(engine, read_sql(path), query_params)
        _assert_near(grouped["sales"].sum(), kpi["sales"], f"{label} sales")
        _assert_near(grouped["profit"].sum(), kpi["profit"], f"{label} profit")
        print(f"  OK dashboard {label}: sales and profit agree with KPI")
    if params["category"] is None:
        for label, path, sales_column, profit_column in (
            ("ROLL-UP", "gold/marts/olap_rollup.sql", "total_sales", "total_profit"),
            ("CUBE", "gold/marts/olap_cube.sql", "sales", "profit"),
        ):
            grouped = query_sql(engine, read_sql(path), params)
            total = grouped[grouped["year_total"] == 1]
            if label == "ROLL-UP":
                total = total[(total["quarter_total"] == 1) &
                              (total["market_total"] == 1) &
                              (total["country_total"] == 1)]
            else:
                total = total[(total["category_total"] == 1) &
                              (total["market_total"] == 1)]
            if len(total) != 1:
                raise AssertionError(f"{label}: expected exactly one grand total")
            _assert_near(total.iloc[0][sales_column], kpi["sales"], f"{label} sales")
            _assert_near(total.iloc[0][profit_column], kpi["profit"], f"{label} profit")
            print(f"  OK {label} grand total agrees with KPI")
    print(f"  KPI: {int(kpi['line_count'])} lines, {int(kpi['order_count'])} orders")


def run_suite(args):
    database = args.database
    if args.active:
        from src.app.demo_backend import active_database
        database = active_database()
    engine = create_db_engine(database=database)
    try:
        start, end = _selected_dates(engine, args)
        params = _params(start, end, args)
        print(f"Gold database: {engine.url.database}; order dates: {start} to {end}")
        print(f"Scope: market={args.market}, region={args.region}, country={args.country}")
        for title, sql_path in OLAP_QUERIES:
            result = query_sql(engine, read_sql(sql_path), params)
            print(f"\n{title}: {len(result)} rows")
            print(result.head(5).to_string(index=False))
        if args.check_dashboard:
            print("\nDashboard reconciliation:")
            check_dashboard(engine, params)
    finally:
        engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", help="First order date, YYYY-MM-DD")
    parser.add_argument("--end", help="Last order date, YYYY-MM-DD")
    parser.add_argument("--market")
    parser.add_argument("--region")
    parser.add_argument("--country")
    parser.add_argument("--category")
    parser.add_argument("--metric", choices=("quantity", "sales"), default="sales")
    parser.add_argument("--top-n", type=int, default=5)
    parser.add_argument("--row-limit", type=int, default=20)
    parser.add_argument("--year", type=int, help="Year shown in the pivot")
    parser.add_argument("--database", help="Database name; defaults to DB_NAME")
    parser.add_argument("--active", action="store_true", help="Use active UI demo database")
    parser.add_argument("--check-dashboard", action="store_true",
                        help="Reconcile selected-scope UI aggregates")
    args = parser.parse_args()
    if args.active and args.database:
        parser.error("--active and --database cannot be combined")
    run_suite(args)


if __name__ == "__main__":
    main()
