# Gold Fact Loading

## Purpose

Load transactional measures from Silver into Gold Fact tables.

## Files

| File | Responsibility |
|---|---|
| `load_fact_sales.sql` | Load sales transaction records and resolve their corresponding Dimension surrogate keys. |

## Design Notes

- `fact_sales` has a grain of one source order line.
- Resolve Dimension keys using their natural/business keys.
- Keep Order ID as a degenerate dimension if no separate Order Dimension is required.
- Do not aggregate transactions during Fact loading.
- Validate row counts and measures after loading.