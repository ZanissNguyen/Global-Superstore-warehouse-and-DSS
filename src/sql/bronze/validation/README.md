# Bronze Data Validation

## Purpose

Define SQL queries for checking the structural integrity and ingestion completeness of raw data stored in the Bronze layer.

## Files

| File | Responsibility |
|---|---|
| `check_ingestion.sql` | Check ingestion metadata, including batch status, imported filename, and recorded row count. |
| `check_row_count.sql` | Compare the number of records stored in the raw table against the number recorded for the corresponding ingestion batch. |
| `check_duplicates.sql` | Identify duplicate source records within an ingestion batch. |
| `check_schema.sql` | Inspect the raw table structure and verify that required source columns are available. |

## Design Notes

- Validate ingestion completeness before proceeding to Silver.
- Use the ingestion identifier to scope validation to a specific batch.
- Do not clean, update, or remove raw records during validation.
- Preserve the original imported data for traceability and reprocessing.
- Validation failures should be reported and logged with the corresponding ingestion identifier.