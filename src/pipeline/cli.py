import argparse
from pathlib import Path


def create_parser(description: str = "ETL Pipeline"):
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional input file or directory path"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Execute without committing changes"
    )

    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Execute SQL then rollback"
    )

    return parser


def parse_args(description: str = "ETL Pipeline"):
    parser = create_parser(description)
    args = parser.parse_args()

    if args.rollback and not args.dry_run:
        parser.error("--rollback requires --dry-run")

    return args