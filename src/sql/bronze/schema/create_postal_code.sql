CREATE TABLE IF NOT EXISTS bronze.postal_code (
    "Country" TEXT,
    "City" TEXT,
    "State" TEXT,
    "Postal Code" TEXT,
    "ingestion" INTEGER,

    CONSTRAINT uq_postal_code
        UNIQUE ("Country", "City", "State", "Postal Code")
);
