// =============================================================================
// POWER QUERY (M CODE) - POSTGRESQL DATA CONNECTOR SCRIPTS
// Database: global_superstore | Host: localhost:5432 (hoặc 5433)
// =============================================================================

// -----------------------------------------------------------------------------
// 1. gold.dim_date
// -----------------------------------------------------------------------------
let
    Source = PostgreSQL.Database("localhost:5432", "global_superstore"),
    gold_dim_date = Source{[Schema="gold",Item="dim_date"]}[Data]
in
    gold_dim_date

// -----------------------------------------------------------------------------
// 2. gold.dim_customer
// -----------------------------------------------------------------------------
let
    Source = PostgreSQL.Database("localhost:5432", "global_superstore"),
    gold_dim_customer = Source{[Schema="gold",Item="dim_customer"]}[Data]
in
    gold_dim_customer

// -----------------------------------------------------------------------------
// 3. gold.dim_product
// -----------------------------------------------------------------------------
let
    Source = PostgreSQL.Database("localhost:5432", "global_superstore"),
    gold_dim_product = Source{[Schema="gold",Item="dim_product"]}[Data]
in
    gold_dim_product

// -----------------------------------------------------------------------------
// 4. gold.dim_geography
// -----------------------------------------------------------------------------
let
    Source = PostgreSQL.Database("localhost:5432", "global_superstore"),
    gold_dim_geography = Source{[Schema="gold",Item="dim_geography"]}[Data]
in
    gold_dim_geography

// -----------------------------------------------------------------------------
// 5. gold.dim_ship_mode
// -----------------------------------------------------------------------------
let
    Source = PostgreSQL.Database("localhost:5432", "global_superstore"),
    gold_dim_ship_mode = Source{[Schema="gold",Item="dim_ship_mode"]}[Data]
in
    gold_dim_ship_mode

// -----------------------------------------------------------------------------
// 6. gold.fact_sales
// -----------------------------------------------------------------------------
let
    Source = PostgreSQL.Database("localhost:5432", "global_superstore"),
    gold_fact_sales = Source{[Schema="gold",Item="fact_sales"]}[Data]
in
    gold_fact_sales

// -----------------------------------------------------------------------------
// 7. dss.association_rule
// -----------------------------------------------------------------------------
let
    Source = PostgreSQL.Database("localhost:5432", "global_superstore"),
    dss_association_rule = Source{[Schema="dss",Item="association_rule"]}[Data]
in
    dss_association_rule

// -----------------------------------------------------------------------------
// 8. dss.forecast_result
// -----------------------------------------------------------------------------
let
    Source = PostgreSQL.Database("localhost:5432", "global_superstore"),
    dss_forecast_result = Source{[Schema="dss",Item="forecast_result"]}[Data]
in
    dss_forecast_result
