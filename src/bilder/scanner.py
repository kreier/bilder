"""Filesystem scanner for the Bilder Phase-1 catalogue."""

from __future__ import annotations

import argparse
import hashlib
import mimetypes
import sys
from datetime import datetime, timezone
from pathlib import Path

from .database import (
    connect,
    create_file_observation,
    create_scan_session,
    create_source,
    finish_scan_session,
    get_or_create_file_version,
    get_or_create_source_copy,
    initialize_database,
)


SCANNER_VERSION = "0.1.0"


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Calculate the SHA-256 hash of a file."""

    digest = hashlib.sha256()

    with path.open("rb") as file:
        while chunk := file.read(chunk_size):
            digest.update(chunk)

    return digest.hexdigest()


def filesystem_timestamp(timestamp: float) -> str:
    """Convert a filesystem timestamp to an ISO-8601 UTC string."""

    return datetime.fromtimestamp(
        timestamp,
        tz=timezone.utc,
    ).isoformat()


def determine_file_type(path: Path) -> str:
    """Determine a basic MIME type from the filename."""

    file_type, _ = mimetypes.guess_type(path.name)

    return file_type or "application/octet-stream"


def scan(
    database_path: str | Path,
    source_path: str | Path,
    source_name: str | None = None,
) -> int:
    """Scan a filesystem tree and record its observations.

    Returns the ScanSession ID.
    """

    root = Path(source_path).expanduser().resolve()

    if not root.exists():
        raise FileNotFoundError(f"Source path does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Source path is not a directory: {root}")

    source_name = source_name or root.name

    connection = connect(database_path)

    try:
        initialize_database(connection)

        source_id = create_source(
            connection,
            name=source_name,
            source_type="filesystem",
            identity=str(root),
        )

        scan_session_id = create_scan_session(
            connection,
            source_id=source_id,
            scan_root=str(root),
            scanner_version=SCANNER_VERSION,
        )

        try:
            for path in sorted(root.rglob("*")):
                if not path.is_file():
                    continue

                relative_path = path.relative_to(root)

                stat = path.stat()

                size = stat.st_size
                mtime = filesystem_timestamp(stat.st_mtime)
                ctime = filesystem_timestamp(stat.st_ctime)
                file_type = determine_file_type(path)

                digest = sha256_file(path)

                file_version_id = get_or_create_file_version(
                    connection,
                    sha256=digest,
                    size=size,
                )

                get_or_create_source_copy(
                    connection,
                    source_id=source_id,
                    file_version_id=file_version_id,
                )

                create_file_observation(
                    connection,
                    scan_session_id=scan_session_id,
                    source_id=source_id,
                    path=str(relative_path),
                    filename=path.name,
                    size=size,
                    filesystem_mtime=mtime,
                    filesystem_ctime=ctime,
                    file_type=file_type,
                    sha256=digest,
                    file_version_id=file_version_id,
                    classification="discovered",
                )

                print(
                    f"{relative_path} "
                    f"{size} bytes "
                    f"{digest}"
                )

        except Exception:
            finish_scan_session(
                connection,
                scan_session_id,
                status="failed",
            )
            raise

        finish_scan_session(
            connection,
            scan_session_id,
            status="completed",
        )

        return scan_session_id

    finally:
        connection.close()


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""

    parser = argparse.ArgumentParser(
        prog="bilder",
        description="Bilder Phase-1 filesystem scanner",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan a filesystem directory",
    )

    scan_parser.add_argument(
        "source",
        type=Path,
        help="Directory to scan",
    )

    scan_parser.add_argument(
        "--database",
        type=Path,
        default=Path("bilder.db"),
        help="SQLite database path (default: bilder.db)",
    )

    scan_parser.add_argument(
        "--source-name",
        help="Name of the source in the catalogue",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        try:
            session_id = scan(
                database_path=args.database,
                source_path=args.source,
                source_name=args.source_name,
            )

            print()
            print(f"Scan completed: session {session_id}")
            print(f"Database: {args.database}")

            return 0

        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
