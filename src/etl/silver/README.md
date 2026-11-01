# Silver ETL

## Purpose

Transform raw data from the Bronze layer into clean, standardized, and validated data for analytical modeling in Gold.

Silver maintains the source dataset's row-level structure. It does not split the dataset into separate business entities or implement the Star Schema.

## Responsibilities

- Read data from `bronze.orders`.
- Clean and standardize column names and data types.
- Normalize date, numeric, and categorical values.
- Handle missing values and invalid records according to defined rules.
- Validate duplicate records and data consistency.
- Load the transformed data into `silver.orders`.
- Log transformation results and errors.

## Files

| File | Responsibility |
|---|---|
| `transform.py` | Orchestrate the Silver transformation process, reading Bronze data and loading transformed records into Silver. |
| `validate.py` | Execute data quality checks and report validation results. |

## Execution Flow

1. Read data from Bronze.
2. Apply cleaning and standardization.
3. Run data quality validation.
4. Load valid data into `silver.orders`.
5. Record execution results in logs/audit metadata.

## Design Notes

- Preserve the source record grain.
- Do not aggregate data in Silver.
- Do not create analytical Fact or Dimension tables in Silver.
- Keep business metrics and analytical calculations for Gold or the Analytics layer.