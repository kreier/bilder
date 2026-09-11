"""FastAPI application for the Bilder web interface."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..database import connect, count_rows


DATABASE_PATH = Path(
    os.environ.get("BILDER_DATABASE", "bilder.db")
)


app = FastAPI(
    title="Bilder API",
    version="0.1.0",
)


# Vite's development server runs on port 5173 by default.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    """Return a simple API health status."""

    return {
        "status": "ok",
        "application": "bilder",
    }


@app.get("/api/overview")
def overview() -> dict:
    """Return the current catalogue overview."""

    connection = connect(DATABASE_PATH)

    try:
        counts = {
            "sources": count_rows(connection, "source"),
            "scan_sessions": count_rows(connection, "scan_session"),
            "file_versions": count_rows(connection, "file_version"),
            "source_copies": count_rows(connection, "source_copy"),
            "file_observations": count_rows(
                connection,
                "file_observation",
            ),
        }

        latest_scan = connection.execute(
            """
            SELECT
                scan_session.id,
                scan_session.started_at,
                scan_session.completed_at,
                scan_session.status,
                scan_session.scan_root,
                scan_session.scanner_version,
                source.name AS source_name
            FROM scan_session
            JOIN source
                ON source.id = scan_session.source_id
            ORDER BY scan_session.id DESC
            LIMIT 1
            """
        ).fetchone()

        return {
            "database": str(DATABASE_PATH),
            "counts": counts,
            "latest_scan": (
                dict(latest_scan)
                if latest_scan is not None
                else None
            ),
        }

    finally:
        connection.close()