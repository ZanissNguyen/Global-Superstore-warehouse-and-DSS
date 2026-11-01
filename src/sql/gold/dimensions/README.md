# Gold Dimension Loading

## Purpose

Load and maintain Dimension records from Silver data.

## Files

| File | Responsibility |
|---|---|
| `load_dim_date.sql` | Populate the Date Dimension for the required date range. |
| `load_dim_customer.sql` | Load distinct customer records. |
| `load_dim_product.sql` | Load distinct product records. |
| `load_dim_geography.sql` | Load distinct geographical records. |
| `load_dim_ship_mode.sql` | Load distinct shipping modes. |

## Design Notes

- Load Dimensions before Fact tables.
- Generate or maintain surrogate keys.
- Avoid duplicate business-key records.
- Handle unknown or missing Dimension members consistently.
- Ensure the loading strategy supports repeatable ETL execution.