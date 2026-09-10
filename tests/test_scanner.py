"""Tests for the Bilder Phase-1 filesystem scanner."""

import hashlib

from bilder.database import connect, count_rows
from bilder.scanner import scan, sha256_file


def test_sha256_file(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"hello Bilder")

    expected = hashlib.sha256(
        b"hello Bilder"
    ).hexdigest()

    assert sha256_file(test_file) == expected


def test_scan_finds_files(tmp_path):
    source = tmp_path / "source"
    source.mkdir()

    (source / "one.txt").write_text(
        "one",
        encoding="utf-8",
    )

    (source / "two.txt").write_text(
        "two",
        encoding="utf-8",
    )

    nested = source / "nested"
    nested.mkdir()

    (nested / "three.txt").write_text(
        "three",
        encoding="utf-8",
    )

    database_path = tmp_path / "bilder.db"

    session_id = scan(
        database_path=database_path,
        source_path=source,
        source_name="Test source",
    )

    assert session_id == 1

    connection = connect(database_path)

    try:
        assert count_rows(connection, "source") == 1
        assert count_rows(connection, "scan_session") == 1
        assert count_rows(connection, "file_observation") == 3
        assert count_rows(connection, "file_version") == 3
        assert count_rows(connection, "source_copy") == 3

        rows = connection.execute(
            """
            SELECT path, filename, size, sha256
            FROM file_observation
            ORDER BY path
            """
        ).fetchall()

        assert [row["path"] for row in rows] == [
            "nested/three.txt",
            "one.txt",
            "two.txt",
        ]

        assert rows[0]["filename"] == "three.txt"
        assert rows[1]["filename"] == "one.txt"
        assert rows[2]["filename"] == "two.txt"

    finally:
        connection.close()


def test_scan_same_files_twice(tmp_path):
    """The same bytes should result in one FileVersion and one SourceCopy."""

    source = tmp_path / "source"
    source.mkdir()

    (source / "photo.jpg").write_bytes(
        b"fake JPEG data"
    )

    database_path = tmp_path / "bilder.db"

    first_session = scan(
        database_path=database_path,
        source_path=source,
        source_name="Test source",
    )

    second_session = scan(
        database_path=database_path,
        source_path=source,
        source_name="Test source",
    )

    assert first_session == 1
    assert second_session == 2

    connection = connect(database_path)

    try:
        # Two observations because the file was observed twice.
        assert count_rows(
            connection,
            "file_observation",
        ) == 2

        # But the bytes represent only one FileVersion.
        assert count_rows(
            connection,
            "file_version",
        ) == 1

        # And there is only one physical source/file-version relationship.
        assert count_rows(
            connection,
            "source_copy",
        ) == 1

        assert count_rows(
            connection,
            "scan_session",
        ) == 2

    finally:
        connection.close()


def test_scan_detects_changed_file(tmp_path):
    source = tmp_path / "source"
    source.mkdir()

    test_file = source / "photo.jpg"
    test_file.write_bytes(b"version one")

    database_path = tmp_path / "bilder.db"

    scan(
        database_path=database_path,
        source_path=source,
        source_name="Test source",
    )

    test_file.write_bytes(b"version two")

    scan(
        database_path=database_path,
        source_path=source,
        source_name="Test source",
    )

    connection = connect(database_path)

    try:
        # Two observations: one for each scan.
        assert count_rows(
            connection,
            "file_observation",
        ) == 2

        # Two different byte-level versions.
        assert count_rows(
            connection,
            "file_version",
        ) == 2

        # Both versions have been observed at the same source.
        assert count_rows(
            connection,
            "source_copy",
        ) == 2

    finally:
        connection.close()
