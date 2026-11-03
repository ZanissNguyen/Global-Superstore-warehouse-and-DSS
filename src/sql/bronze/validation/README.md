# Bronze Data Validation

## Purpose

Define SQL queries for checking the structural integrity and ingestion completeness of raw data stored in the Bronze layer.

## Files

| File | Responsibility |
|---|---|
| `check_row_count.sql` | Compare the number of records stored in the raw table against the number recorded for the corresponding ingestion batch. |
| `check_duplicates.sql` | Identify duplicate source records within an ingestion batch. |

## Design Notes

- Validate ingestion completeness before proceeding to Silver.
- Use the ingestion identifier to scope validation to a specific batch.
- Do not clean, update, or remove raw records during validation.
- Preserve the original imported data for traceability and reprocessing.
- Validation failures should be reported and logged with the corresponding ingestion identifier.