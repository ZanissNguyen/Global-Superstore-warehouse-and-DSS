
from pathlib import Path

# src/pipeline/config.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
LOG_DIR = PROJECT_ROOT / "logs"


def ensure_directories() -> None:
    """Create standard directories when needed."""
    for directory in (RAW_DIR, PROCESSED_DIR, LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)
