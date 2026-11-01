# Silver Data Validation

## Purpose

Define SQL queries for checking the quality and consistency of Silver data.

## Files

| File | Responsibility |
|---|---|
| `check_nulls.sql` | Identify NULL values in required columns. |
| `check_duplicates.sql` | Detect duplicate records based on the defined source record key. |
| `check_data_quality.sql` | Check invalid values, data types, date consistency, and business-rule violations. |

## Design Notes

- Validation queries should report issues rather than silently modify data.
- Define which columns are mandatory and which can legitimately contain NULL.
- Record validation results for each ETL execution.