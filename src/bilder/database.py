"""SQLite database handling for the Bilder Phase-1 catalogue."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS source (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    source_type     TEXT NOT NULL,
    identity        TEXT,
    description     TEXT,
    created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    retired_at      TEXT
);

CREATE TABLE IF NOT EXISTS scan_session (
    id              INTEGER PRIMARY KEY,
    source_id       INTEGER NOT NULL,
    started_at      TEXT NOT NULL,
    completed_at    TEXT,
    status          TEXT NOT NULL,
    scan_root       TEXT NOT NULL,
    scanner_version TEXT NOT NULL,

    FOREIGN KEY (source_id) REFERENCES source(id),

    CHECK (status IN (
        'running',
        'completed',
        'failed',
        'cancelled',
        'partial'
    ))
);

CREATE TABLE IF NOT EXISTS file_version (
    id              INTEGER PRIMARY KEY,
    sha256          TEXT NOT NULL UNIQUE,
    size            INTEGER NOT NULL,
    first_seen_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS source_copy (
    id              INTEGER PRIMARY KEY,
    source_id       INTEGER NOT NULL,
    file_version_id INTEGER NOT NULL,
    first_seen_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at    TEXT,
    state           TEXT NOT NULL DEFAULT 'present',

    FOREIGN KEY (source_id) REFERENCES source(id),
    FOREIGN KEY (file_version_id) REFERENCES file_version(id),

    CHECK (state IN (
        'present',
        'missing',
        'deleted',
        'unknown'
    )),

    UNIQUE (source_id, file_version_id)
);

CREATE TABLE IF NOT EXISTS file_observation (
    id                  INTEGER PRIMARY KEY,
    scan_session_id     INTEGER NOT NULL,
    source_id           INTEGER NOT NULL,

    path                TEXT NOT NULL,
    filename            TEXT NOT NULL,

    size                INTEGER NOT NULL,

    filesystem_mtime    TEXT,
    filesystem_ctime    TEXT,

    file_type           TEXT,

    sha256              TEXT,
    file_version_id     INTEGER,

    observed_at         TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    classification      TEXT,

    FOREIGN KEY (scan_session_id) REFERENCES scan_session(id),
    FOREIGN KEY (source_id) REFERENCES source(id),
    FOREIGN KEY (file_version_id) REFERENCES file_version(id)
);

CREATE INDEX IF NOT EXISTS idx_scan_session_source
    ON scan_session(source_id);

CREATE INDEX IF NOT EXISTS idx_file_observation_scan
    ON file_observation(scan_session_id);

CREATE INDEX IF NOT EXISTS idx_file_observation_source_path
    ON file_observation(source_id, path);

CREATE INDEX IF NOT EXISTS idx_file_observation_sha256
    ON file_observation(sha256);

CREATE INDEX IF NOT EXISTS idx_source_copy_source
    ON source_copy(source_id);

CREATE INDEX IF NOT EXISTS idx_source_copy_version
    ON source_copy(file_version_id);
"""


def connect(database_path: str | Path) -> sqlite3.Connection:
    """Open a Bilder SQLite database connection."""

    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database(connection: sqlite3.Connection) -> None:
    """Create the Phase-1 database schema if it does not exist."""

    connection.executescript(SCHEMA)
    connection.commit()


def create_source(
    connection: sqlite3.Connection,
    name: str,
    source_type: str = "filesystem",
    identity: str | None = None,
    description: str | None = None,
) -> int:
    """Create a source and return its database ID."""

    cursor = connection.execute(
        """
        INSERT INTO source (
            name,
            source_type,
            identity,
            description
        )
        VALUES (?, ?, ?, ?)
        """,
        (name, source_type, identity, description),
    )

    connection.commit()
    return int(cursor.lastrowid)


def get_source(
    connection: sqlite3.Connection,
    source_id: int,
) -> sqlite3.Row | None:
    """Return a source by ID."""

    return connection.execute(
        """
        SELECT *
        FROM source
        WHERE id = ?
        """,
        (source_id,),
    ).fetchone()


def create_scan_session(
    connection: sqlite3.Connection,
    source_id: int,
    scan_root: str,
    scanner_version: str,
) -> int:
    """Create a running scan session and return its ID."""

    cursor = connection.execute(
        """
        INSERT INTO scan_session (
            source_id,
            started_at,
            status,
            scan_root,
            scanner_version
        )
        VALUES (
            ?,
            CURRENT_TIMESTAMP,
            'running',
            ?,
            ?
        )
        """,
        (source_id, scan_root, scanner_version),
    )

    connection.commit()
    return int(cursor.lastrowid)


def finish_scan_session(
    connection: sqlite3.Connection,
    scan_session_id: int,
    status: str = "completed",
) -> None:
    """Finish a scan session."""

    if status not in {
        "completed",
        "failed",
        "cancelled",
        "partial",
    }:
        raise ValueError(f"Invalid scan status: {status}")

    connection.execute(
        """
        UPDATE scan_session
        SET completed_at = CURRENT_TIMESTAMP,
            status = ?
        WHERE id = ?
        """,
        (status, scan_session_id),
    )

    connection.commit()


def get_or_create_file_version(
    connection: sqlite3.Connection,
    sha256: str,
    size: int,
) -> int:
    """Return the FileVersion ID for a SHA-256 hash.

    A SHA-256 hash identifies the exact byte-level FileVersion.
    """

    row = connection.execute(
        """
        SELECT id
        FROM file_version
        WHERE sha256 = ?
        """,
        (sha256,),
    ).fetchone()

    if row is not None:
        return int(row["id"])

    cursor = connection.execute(
        """
        INSERT INTO file_version (
            sha256,
            size
        )
        VALUES (?, ?)
        """,
        (sha256, size),
    )

    connection.commit()
    return int(cursor.lastrowid)


def get_or_create_source_copy(
    connection: sqlite3.Connection,
    source_id: int,
    file_version_id: int,
) -> int:
    """Return the SourceCopy ID for a source/file-version pair."""

    row = connection.execute(
        """
        SELECT id
        FROM source_copy
        WHERE source_id = ?
          AND file_version_id = ?
        """,
        (source_id, file_version_id),
    ).fetchone()

    if row is not None:
        connection.execute(
            """
            UPDATE source_copy
            SET last_seen_at = CURRENT_TIMESTAMP,
                state = 'present'
            WHERE id = ?
            """,
            (row["id"],),
        )
        connection.commit()
        return int(row["id"])

    cursor = connection.execute(
        """
        INSERT INTO source_copy (
            source_id,
            file_version_id,
            first_seen_at,
            last_seen_at,
            state
        )
        VALUES (
            ?,
            ?,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP,
            'present'
        )
        """,
        (source_id, file_version_id),
    )

    connection.commit()
    return int(cursor.lastrowid)


def create_file_observation(
    connection: sqlite3.Connection,
    *,
    scan_session_id: int,
    source_id: int,
    path: str,
    filename: str,
    size: int,
    filesystem_mtime: str | None,
    filesystem_ctime: str | None,
    file_type: str | None,
    sha256: str | None,
    file_version_id: int | None,
    classification: str | None = None,
) -> int:
    """Create a FileObservation."""

    cursor = connection.execute(
        """
        INSERT INTO file_observation (
            scan_session_id,
            source_id,
            path,
            filename,
            size,
            filesystem_mtime,
            filesystem_ctime,
            file_type,
            sha256,
            file_version_id,
            observed_at,
            classification
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?
        )
        """,
        (
            scan_session_id,
            source_id,
            path,
            filename,
            size,
            filesystem_mtime,
            filesystem_ctime,
            file_type,
            sha256,
            file_version_id,
            classification,
        ),
    )

    connection.commit()
    return int(cursor.lastrowid)


def count_rows(
    connection: sqlite3.Connection,
    table: str,
) -> int:
    """Return the number of rows in a known Bilder table."""

    allowed_tables = {
        "source",
        "scan_session",
        "file_version",
        "source_copy",
        "file_observation",
    }

    if table not in allowed_tables:
        raise ValueError(f"Unknown table: {table}")

    row = connection.execute(
        f"SELECT COUNT(*) AS count FROM {table}"
    ).fetchone()

    return int(row["count"])


def fetch_all(
    connection: sqlite3.Connection,
    table: str,
) -> list[dict[str, Any]]:
    """Return all rows from a known Bilder table as dictionaries."""

    allowed_tables = {
        "source",
        "scan_session",
        "file_version",
        "source_copy",
        "file_observation",
    }

    if table not in allowed_tables:
        raise ValueError(f"Unknown table: {table}")

    rows = connection.execute(
        f"SELECT * FROM {table} ORDER BY id"
    ).fetchall()

    return [dict(row) for row in rows]