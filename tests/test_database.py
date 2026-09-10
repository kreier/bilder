"""Tests for the Bilder Phase-1 database."""

from bilder.database import (
    connect,
    count_rows,
    create_file_observation,
    create_scan_session,
    create_source,
    finish_scan_session,
    get_or_create_file_version,
    get_or_create_source_copy,
    initialize_database,
)


def test_database_initialization(tmp_path):
    database_path = tmp_path / "test.db"

    connection = connect(database_path)

    try:
        initialize_database(connection)

        assert count_rows(connection, "source") == 0
        assert count_rows(connection, "scan_session") == 0
        assert count_rows(connection, "file_version") == 0
        assert count_rows(connection, "source_copy") == 0
        assert count_rows(connection, "file_observation") == 0

    finally:
        connection.close()


def test_create_source_and_scan_session(tmp_path):
    database_path = tmp_path / "test.db"

    connection = connect(database_path)

    try:
        initialize_database(connection)

        source_id = create_source(
            connection,
            name="Test source",
        )

        session_id = create_scan_session(
            connection,
            source_id=source_id,
            scan_root="/test/source",
            scanner_version="0.1.0",
        )

        finish_scan_session(
            connection,
            session_id,
        )

        assert count_rows(connection, "source") == 1
        assert count_rows(connection, "scan_session") == 1

        row = connection.execute(
            """
            SELECT status
            FROM scan_session
            WHERE id = ?
            """,
            (session_id,),
        ).fetchone()

        assert row["status"] == "completed"

    finally:
        connection.close()


def test_file_version_is_reused_for_same_hash(tmp_path):
    database_path = tmp_path / "test.db"

    connection = connect(database_path)

    try:
        initialize_database(connection)

        first_id = get_or_create_file_version(
            connection,
            sha256="abc123",
            size=100,
        )

        second_id = get_or_create_file_version(
            connection,
            sha256="abc123",
            size=100,
        )

        assert first_id == second_id
        assert count_rows(connection, "file_version") == 1

    finally:
        connection.close()


def test_source_copy_is_reused(tmp_path):
    database_path = tmp_path / "test.db"

    connection = connect(database_path)

    try:
        initialize_database(connection)

        source_id = create_source(
            connection,
            name="Test source",
        )

        file_version_id = get_or_create_file_version(
            connection,
            sha256="abc123",
            size=100,
        )

        first_id = get_or_create_source_copy(
            connection,
            source_id,
            file_version_id,
        )

        second_id = get_or_create_source_copy(
            connection,
            source_id,
            file_version_id,
        )

        assert first_id == second_id
        assert count_rows(connection, "source_copy") == 1

    finally:
        connection.close()


def test_file_observation(tmp_path):
    database_path = tmp_path / "test.db"

    connection = connect(database_path)

    try:
        initialize_database(connection)

        source_id = create_source(
            connection,
            name="Test source",
        )

        session_id = create_scan_session(
            connection,
            source_id=source_id,
            scan_root="/test/source",
            scanner_version="0.1.0",
        )

        file_version_id = get_or_create_file_version(
            connection,
            sha256="abc123",
            size=100,
        )

        observation_id = create_file_observation(
            connection,
            scan_session_id=session_id,
            source_id=source_id,
            path="photos/test.jpg",
            filename="test.jpg",
            size=100,
            filesystem_mtime="2026-09-10T00:00:00+00:00",
            filesystem_ctime="2026-09-10T00:00:00+00:00",
            file_type="image/jpeg",
            sha256="abc123",
            file_version_id=file_version_id,
            classification="discovered",
        )

        assert observation_id > 0
        assert count_rows(connection, "file_observation") == 1

    finally:
        connection.close()
