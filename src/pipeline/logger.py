
import logging
import time
from datetime import datetime
from functools import wraps
from pathlib import Path

from pipeline.config import LOG_DIR, ensure_directories


def setup_logger(
    name="etl_pipeline",
    run_id="manual",
    log_dir=LOG_DIR,
):
    ensure_directories()
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | "
            "run_id=%(run_id)s | %(message)s"
        )

        file_handler = logging.FileHandler(
            log_dir / f"{name}_{datetime.now():%Y%m%d}.log",
            encoding="utf-8",
        )
        console_handler = logging.StreamHandler()

        for handler in (file_handler, console_handler):
            handler.setFormatter(formatter)
            logger.addHandler(handler)

    return logging.LoggerAdapter(
        logger, {"run_id": run_id}
    )


def log_execution(logger):
    """Decorator: log start, success, failure and duration."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            logger.info("Started: %s", func.__name__)

            try:
                result = func(*args, **kwargs)
                logger.info("Succeeded: %s", func.__name__)
                return result

            except Exception:
                logger.exception("Failed: %s", func.__name__)
                raise

            finally:
                elapsed = time.perf_counter() - start
                logger.info(
                    "Finished: %s | duration=%.2fs",
                    func.__name__,
                    elapsed,
                )

        return wrapper
    return decorator
