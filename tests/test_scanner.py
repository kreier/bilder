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

        # The same physical source copy now points to the latest version.
        assert count_rows(
            connection,
            "source_copy",
        ) == 1

    finally:
        connection.close()

def test_same_file_version_at_two_paths_creates_two_source_copies(tmp_path):
    """Identical bytes at two paths are one FileVersion but two SourceCopies."""

    source = tmp_path / "source"
    source.mkdir()

    data = b"fake JPEG data"

    (source / "photo1.jpg").write_bytes(data)
    (source / "photo2.jpg").write_bytes(data)

    database_path = tmp_path / "bilder.db"

    scan(
        database_path=database_path,
        source_path=source,
        source_name="Test source",
    )

    connection = connect(database_path)

    try:
        # Two physical files contain the same bytes.
        assert count_rows(
            connection,
            "file_observation",
        ) == 2

        # But there is only one unique byte-level FileVersion.
        assert count_rows(
            connection,
            "file_version",
        ) == 1

        # There should be two physical occurrences.
        assert count_rows(
            connection,
            "source_copy",
        ) == 2

    finally:
        connection.close()

def test_scan_marks_deleted_file_missing_and_restores_it(tmp_path):
    """A deleted file becomes missing and can later return as present."""

    source = tmp_path / "source"
    source.mkdir()

    test_file = source / "photo.jpg"
    test_file.write_bytes(b"photo data")

    database_path = tmp_path / "bilder.db"

    # First scan: the file is present.
    scan(
        database_path=database_path,
        source_path=source,
        source_name="Test source",
    )

    connection = connect(database_path)

    try:
        row = connection.execute(
            """
            SELECT
                file_version_id,
                state
            FROM source_copy
            WHERE path = ?
            """,
            ("photo.jpg",),
        ).fetchone()

        original_file_version_id = row["file_version_id"]

        assert row["state"] == "present"

    finally:
        connection.close()

    # Delete the file.
    test_file.unlink()

    # Second scan: the file is missing.
    scan(
        database_path=database_path,
        source_path=source,
        source_name="Test source",
    )

    connection = connect(database_path)

    try:
        row = connection.execute(
            """
            SELECT
                file_version_id,
                state
            FROM source_copy
            WHERE path = ?
            """,
            ("photo.jpg",),
        ).fetchone()

        assert row["file_version_id"] == original_file_version_id
        assert row["state"] == "missing"

    finally:
        connection.close()

    # Restore the exact same bytes.
    test_file.write_bytes(b"photo data")

    # Third scan: the file is present again.
    scan(
        database_path=database_path,
        source_path=source,
        source_name="Test source",
    )

    connection = connect(database_path)

    try:
        row = connection.execute(
            """
            SELECT
                file_version_id,
                state
            FROM source_copy
            WHERE path = ?
            """,
            ("photo.jpg",),
        ).fetchone()

        assert row["file_version_id"] == original_file_version_id
        assert row["state"] == "present"

        # The three scans should produce two observations:
        # one when present initially and one after restoration.
        assert count_rows(
            connection,
            "file_observation",
        ) == 2

        # The restored file must not create a new FileVersion.
        assert count_rows(
            connection,
            "file_version",
        ) == 1

    finally:
        connection.close()

def test_failed_scan_does_not_mark_existing_files_missing(
    tmp_path,
    monkeypatch,
):
    """A failed scan must not reconcile existing SourceCopies as missing."""

    source = tmp_path / "source"
    source.mkdir()

    existing_file = source / "existing.jpg"
    existing_file.write_bytes(b"existing photo")

    database_path = tmp_path / "bilder.db"

    # First scan: the file is present.
    scan(
        database_path=database_path,
        source_path=source,
        source_name="Test source",
    )

    # Make the scanner fail during the second scan.
    def failing_sha256_file(path):
        raise RuntimeError("simulated scan failure")

    monkeypatch.setattr(
        "bilder.scanner.sha256_file",
        failing_sha256_file,
    )

    try:
        scan(
            database_path=database_path,
            source_path=source,
            source_name="Test source",
        )
    except RuntimeError as exc:
        assert str(exc) == "simulated scan failure"
    else:
        raise AssertionError("Expected scan to fail")

    connection = connect(database_path)

    try:
        # The failed scan must not have marked the existing file missing.
        row = connection.execute(
            """
            SELECT state
            FROM source_copy
            WHERE path = ?
            """,
            ("existing.jpg",),
        ).fetchone()

        assert row["state"] == "present"

        # The failed scan itself should be recorded as failed.
        row = connection.execute(
            """
            SELECT status
            FROM scan_session
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()

        assert row["status"] == "failed"

    finally:
        connection.close()
