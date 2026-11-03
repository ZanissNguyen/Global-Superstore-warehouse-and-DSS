CREATE TABLE IF NOT EXISTS bronze.market (
    "Country" TEXT,
    "Market" TEXT,
    "ingestion" INTEGER,

    CONSTRAINT uq_market
        UNIQUE ("Country", "Market")
);
