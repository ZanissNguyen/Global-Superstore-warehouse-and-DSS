# Bronze Schema

## Purpose

Define the database structure for storing raw data ingested from external source files.

## Files

| File | Responsibility |
|---|---|
| `create_ingestion.sql` | Create the ingestion metadata table to track imported files, execution information, and ingestion status. |
| `create_raw_orders.sql` | Create the raw orders table for storing records imported from the source dataset. |

## Design Notes

- Preserve the original source data structure as much as possible.
- Keep raw records separate from ingestion metadata.
- Include an ingestion identifier to associate each raw record with its import batch.
- Avoid applying business transformations or aggregations at this layer.
- Use appropriate data types while minimizing unintended data modification during ingestion.