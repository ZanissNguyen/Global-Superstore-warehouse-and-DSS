# Gold ETL

## Purpose

Transform clean Silver data into an analytical Star Schema for reporting, business analysis, and Decision Support Systems (DSS).

## Responsibilities

- Extract data from `silver.orders`.
- Load Dimension tables.
- Generate surrogate keys and resolve business-key relationships.
- Load Fact tables at the defined grain.
- Validate referential integrity and aggregate consistency.

## Files

| File | Responsibility |
|---|---|
| `load_dimensions.py` | Coordinate loading of all Dimension tables. |
| `load_facts.py` | Load Fact tables after the required Dimensions are available. |
| `validate.py` | Execute Gold-layer validation checks. |

## Execution Flow

1. Load Dimensions.
2. Resolve Dimension surrogate keys.
3. Load Fact tables.
4. Validate foreign keys and fact grain.
5. Compare key aggregates against Silver.

## Design Notes

- Gold is where the Star Schema is introduced.
- Fact tables must have explicitly documented grains.
- Use surrogate keys for Dimension relationships.
- Avoid duplicating the same business metrics across unnecessary Fact tables.