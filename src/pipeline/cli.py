
import argparse


def create_parser(description: str = "ETL Pipeline"):
    parser = argparse.ArgumentParser(
        description=description
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Execute without committing changes"
    )

    parser.add_argument(
        "--rollback-test",
        action="store_true",
        help="Execute SQL then rollback"
    )

    return parser


def parse_args(description: str = "ETL Pipeline"):
    parser = create_parser(description)
    args = parser.parse_args()

    if args.rollback_test and not args.dry_run:
        parser.error("--rollback-test requires --dry-run")

    return args
