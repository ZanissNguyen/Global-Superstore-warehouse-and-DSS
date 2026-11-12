# Gold analytics and data marts

### OLAP queries used by the UI

The `gold/dashboard/*.sql` files are the canonical OLAP queries for the
`Tong quan kinh doanh` tab. They implement date/geography slicing, time and
product/geography roll-up, drill-down, Top N and loss analysis. All UI queries
read Gold fact/dimension tables so arbitrary order-date ranges and geographic
filters retain their exact meaning. The app loads these files with
`pipeline.reader.read_sql()`; no UI chart reads a materialized view directly.

The seven `olap_*.sql` files here are parameterized demonstrations of OLAP
operators. `run_olap_suite.py` passes the same date/geography scope used by the
UI. Pivot, MoM and Cube remain supplementary examples; they are not UI charts.

From the repository root, run for the base database:

```text
python -m src.sql.gold.marts.run_olap_suite --check-dashboard
```

For the currently active uploaded-data session, use `--active`. Use
`--start 2014-03-05 --end 2014-09-17 --market APAC` to check a custom slice.
The checker compares additive sales and profit from category, monthly trend,
market and segment queries against the same-scope UI KPI. The date range must
be within the selected Gold database. Do not add pre-aggregated distinct order
counts or average pre-aggregated margins across groups.

`mv_sales_mart` has month-level data and `mv_product_mart` has year/market-level
data. Neither is a drop-in replacement for arbitrary UI date and geography
filters. Materialized views are refreshed after the uploaded file passes ETL
and reconciliation, before the new demo database becomes active.

### Data Marts

- Data Marts are organized around business domains, including Sales, Product, and Customer Analytics.
- Build Data Marts from the shared Gold Fact and Dimension tables rather than duplicating the underlying transactional data.
- Each Data Mart should provide the analytical datasets required by its corresponding business questions and dashboards.
- Data Marts may be implemented as regular Views or Materialized Views, depending on performance and refresh requirements.

### Materialized Views

- Materialized Views store the results of predefined analytical queries for faster data retrieval.
- Define and create Materialized Views separately from the core Fact and Dimension schema.
- Refresh Materialized Views after the Gold ETL process completes successfully.
- Ensure that refresh operations are included in the overall pipeline workflow.
- Avoid refreshing Materialized Views when the upstream Gold data has not been updated successfully.
