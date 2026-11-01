# Gold Data Validation

## Purpose

Validate the correctness and consistency of the Gold Star Schema.

## Files

| File | Responsibility |
|---|---|
| `check_fact_grain.sql` | Check whether Fact records follow the defined grain. |
| `check_foreign_keys.sql` | Identify Fact records with missing or invalid Dimension references. |
| `check_aggregates.sql` | Compare Sales, Profit, Quantity, and other key aggregates against Silver. |

## Design Notes

- Validation should detect missing, duplicated, or inconsistent records.
- Aggregate comparisons must use equivalent filters and granularity.
- Validation results should be traceable to the corresponding ETL execution.