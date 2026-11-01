# Silver Schema

## Purpose

Define the database structure for tables in the Silver layer.

## Files

| File | Responsibility |
|---|---|
| `create_orders.sql` | Create `silver.orders`, which stores cleaned and standardized order-level source records. |

## Design Notes

- Preserve the source dataset's row-level structure.
- Use appropriate PostgreSQL data types.
- Define primary keys or uniqueness constraints only when supported by the source data.
- Do not introduce Fact and Dimension tables here.

