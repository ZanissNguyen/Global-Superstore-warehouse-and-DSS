import pandas as pd
from pathlib import Path
import hashlib

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def read_data(file_path, logger=None):
    """Read CSV or Excel file."""

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    extension = file_path.suffix.lower()

    if extension == ".csv":
        encodings = ["utf-8", "cp1252", "latin1"]

        for encoding in encodings:
            try:
                df = pd.read_csv(
                    file_path,
                    encoding=encoding
                )

                if logger:
                    logger.info(
                        "CSV loaded with encoding: %s",
                        encoding
                    )

                return {
                    "data": df,
                    "encoding": encoding,
                    "file_path": str(file_path)
                }

            except UnicodeDecodeError:
                continue

        raise ValueError(
            f"Cannot decode CSV file: {file_path}"
        )

    elif extension in {".xlsx", ".xls"}:
        df = pd.read_excel(file_path)
        data = {"data": df}

    else:
        raise ValueError(f"Unsupported extension: {extension}")

    if logger:
        logger.info(
            "Read completed: file=%s, tables=%d, rows=%d",
            file_path.name,
            len(data),
            sum(len(df) for df in data.values()),
        )

    return data

def create_content_hash(file_path: str) -> str:
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()

def read_sql(sql_path, logger=None):
    """Read SQL script."""

    sql_path = PROJECT_ROOT / "src" / "sql" / sql_path

    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    if sql_path.suffix.lower() != ".sql":
        raise ValueError(f"Expected .sql file: {sql_path}")

    sql = sql_path.read_text(encoding="utf-8")

    if logger:
        logger.info("SQL loaded: file=%s", sql_path.name)

    return sql