
import datetime as Date
from pandas import DataFrame

from src.pipeline.logger import setup_logger, log_execution
from src.pipeline.reader import read_data, create_content_hash, read_sql

from src.pipeline.executor import query_sql


REQUIRED_COLUMNS = [
    "Row ID",
    "Order ID",
    "Order Date",
    "Ship Date",
    "Ship Mode",
    "Customer ID",
    "Customer Name",
    "Segment",
    "Country",
    "City",
    "State",
    "Region",
    "Product ID",
    "Category",
    "Sub-Category",
    "Product Name",
    "Sales",
    "Quantity",
    "Discount",
    "Profit"
]

OPTIONAL_COLUMNS = [
    "Postal Code",
    "Market",
    "Shipping Cost",
    "Order Priority"
]

ALL_COLUMNS = REQUIRED_COLUMNS + OPTIONAL_COLUMNS

def read_raw_data(input_path: str):
    # load file
    logger = setup_logger(name="bronze",run_id="bronze_001")

    @log_execution(logger)
    def run_extract(file_path):
        return read_data(file_path)

    df = run_extract(input_path)["data"]
    content_hash = create_content_hash(input_path)
    loaded_time = Date.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Data loaded at: {loaded_time}")
    print(f"Content hash: {content_hash}")

    print(df.head(5))
    print(df.shape)
    return df, content_hash, loaded_time

def is_file_extracted(engine, content_hash: str):
    return query_sql(
        engine,
        read_sql("bronze/validation/check_duplicates.sql"),
        {"content_hash": content_hash}
    )["exists"][0]

def valid_data(df: DataFrame):
    checked_df = df.copy()

    missing = [
        col for col in REQUIRED_COLUMNS
        if col not in checked_df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    for col in OPTIONAL_COLUMNS:
        if col not in df.columns:
            checked_df[col] = None

    print(checked_df.shape)
    return checked_df

def extract_market(df):
    if {"Country", "Market"}.issubset(df.columns):
        # get all unique set of Country -> Market
        unique_market = df[["Country", "Market"]].drop_duplicates()
        print('Market extracted', unique_market.head(5))
        market_count = unique_market.shape[0]
        return unique_market, market_count
    else:
        return None, 0

    
def extract_postal_code(df):
    if {"City", "State", "Country", "Postal Code"}.issubset(df.columns):
        # only get the rows that have Postal Code
        have_pin = df[df["Postal Code"].notnull()]
        # get all unique set of  City, State, Country -> Postal Code 
        unique_pin = have_pin[["City", "State", "Country", "Postal Code"]].drop_duplicates()
        print('PIN extracted', unique_pin.head(5))
        pin_count = unique_pin.shape[0]
        return unique_pin, pin_count
    else:
        return None, 0