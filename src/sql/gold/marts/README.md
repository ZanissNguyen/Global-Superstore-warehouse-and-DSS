### Data Marts

- Data Marts are organized around business domains, including Sales, Product, and Customer Analytics.
- Build Data Marts from the shared Gold Fact and Dimension tables rather than duplicating the underlying transactional data.
- Each Data Mart should provide the analytical datasets required by its corresponding business questions and dashboards.
- Data Marts may be implemented as regular Views or Materialized Views, depending on performance and refresh requirements.

### Materialized Views

- Materialized Views store the results of predefined analytical queries for faster data retrieval.
- Define and create Materialized Views separately from the core Fact and Dimension schema.
- Refresh Materialized Views after the Gold ETL process completes successfully.
- Ensure that refresh operations are included in the overall pipeline workflow.
- Avoid refreshing Materialized Views when the upstream Gold data has not been updated successfully.