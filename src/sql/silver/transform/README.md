# Silver Transformation SQL

## Purpose

Define SQL transformations that move and clean data from Bronze into Silver.

## Files

| File | Responsibility |
|---|---|
| `transform_orders.sql` | Transform records from `bronze.orders` into the standardized structure of `silver.orders`. |

## Design Notes

- Standardize data types and formats.
- Handle NULL values and invalid data according to documented rules.
- Avoid aggregating or changing the source record grain.
- Keep transformations reproducible and suitable for repeated execution.