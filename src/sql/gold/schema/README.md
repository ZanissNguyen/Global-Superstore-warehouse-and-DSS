# Gold Schema

## Purpose

Define the Star Schema database structures used by the analytical layer.

## Files

| File | Responsibility |
|---|---|
| `create_dim_date.sql` | Create the Date Dimension. |
| `create_dim_customer.sql` | Create the Customer Dimension. |
| `create_dim_product.sql` | Create the Product Dimension. |
| `create_dim_geography.sql` | Create the Geography Dimension. |
| `create_dim_ship_mode.sql` | Create the Shipping Mode Dimension. |
| `create_fact_sales.sql` | Create the Sales Fact table. |

## Design Notes

### Star Schema

- Fact and Dimension tables use surrogate keys.
- Define the Fact table grain before defining its columns.
- Use role-playing Date Dimension references for Order Date and Ship Date.
- Store additive measures such as Sales, Profit, and Quantity in the Fact table.
- Discount is a rate and should not be summed as an ordinary measure.