# ADR 0001: Phase 2 Relational SQLite Schema

**Status:** Proposed / Accepted  
**Date:** 2026-09-11  
**Deciders:** Bilder Core Architecture  
**Consulted:** `docs/architecture.md`, `docs/data-model.md`, `archive/development/Phase 2A`  

---

## 1. Context

In Phase 1, Bilder used an exploratory SQLite schema consisting of:
- `source`
- `scan_session`
- `file_version` (unique sha256)
- `source_copy` (mapping source + path to file_version)
- `file_observation` (raw observation record per scan)

During Phase 2A, the architecture and conceptual data model were formally frozen (`docs/architecture.md` and `docs/data-model.md`). The conceptual model established:
1. **Logical Photo vs. Physical File:** A `Photo` represents a logical photograph, while a `File` represents a tracked physical filesystem entry. A Photo can have multiple Files (RAW+JPEG, duplicates, different encodings).
2. **FileVersion:** Represents an observed byte state of a File, with SHA-256 content verification.
3. **Findings:** Distinct from cataloged Files, representing unclassified or candidate filesystem objects.
4. **ScanRoot & ScanRun:** Distinct from generic sources; ScanRun records software version, configuration snapshots, and per-root outcomes.
5. **ScanEvent:** Append-only event stream recording meaningful scanner discoveries, changes, missing detections, and errors.
6. **PhotoDerivation:** Explicit directional provenance between source and derived Photos.

This Architecture Decision Record establishes the concrete SQLite DDL schema to implement the Phase 2A model for Phase 2B (Data Inspector) and Phase 2C (Deterministic Scanner).

---

## 2. Decision

We define the Phase 2 SQLite schema with the following tables and invariants:

```sql
PRAGMA foreign_keys = ON;

-- 1. Logical Photo
CREATE TABLE IF NOT EXISTS photo (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    status          TEXT NOT NULL DEFAULT 'active', -- 'active', 'missing', 'quarantined'
    created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (status IN ('active', 'missing', 'quarantined'))
);

-- 2. Physical File (tracked filesystem entity belonging to one Photo)
CREATE TABLE IF NOT EXISTS file (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    photo_id        INTEGER NOT NULL,
    scan_root_id    INTEGER NOT NULL,
    rel_path        TEXT NOT NULL,          -- relative path from scan root
    filename        TEXT NOT NULL,
    state           TEXT NOT NULL DEFAULT 'present', -- 'present', 'missing', 'excluded'
    created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (photo_id) REFERENCES photo(id) ON DELETE RESTRICT,
    FOREIGN KEY (scan_root_id) REFERENCES scan_root(id) ON DELETE RESTRICT,
    UNIQUE(scan_root_id, rel_path),
    CHECK (state IN ('present', 'missing', 'excluded'))
);

-- 3. FileVersion (an observed byte state for a File)
CREATE TABLE IF NOT EXISTS file_version (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id             INTEGER NOT NULL,
    sha256              TEXT NOT NULL,
    size_bytes          INTEGER NOT NULL,
    filesystem_mtime    TEXT NOT NULL,
    observed_at         TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (file_id) REFERENCES file(id) ON DELETE RESTRICT
);

-- 4. Photo Derivation (provenance graph between logical Photos)
CREATE TABLE IF NOT EXISTS photo_derivation (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    derived_photo_id    INTEGER NOT NULL,
    source_photo_id     INTEGER NOT NULL,
    derivation_type     TEXT NOT NULL,      -- 'crop', 'resize', 'retouch', 'composite', 'alternate'
    evidence_json       TEXT,
    created_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (derived_photo_id) REFERENCES photo(id) ON DELETE RESTRICT,
    FOREIGN KEY (source_photo_id) REFERENCES photo(id) ON DELETE RESTRICT,
    UNIQUE(derived_photo_id, source_photo_id, derivation_type)
);

-- 5. ScanRoot (configured filesystem target)
CREATE TABLE IF NOT EXISTS scan_root (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    path                TEXT NOT NULL UNIQUE,
    label               TEXT,
    is_active           INTEGER NOT NULL DEFAULT 1,
    config_json         TEXT,               -- include/exclude patterns, supported extensions
    created_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    retired_at          TEXT
);

-- 6. ScanRun (individual scanner execution)
CREATE TABLE IF NOT EXISTS scan_run (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_root_id        INTEGER NOT NULL,
    status              TEXT NOT NULL,      -- 'running', 'completed', 'failed', 'cancelled', 'partial'
    scanner_version     TEXT NOT NULL,
    config_snapshot     TEXT NOT NULL,      -- serialized effective configuration
    config_hash         TEXT NOT NULL,      -- deterministic hash of configuration
    started_at          TEXT NOT NULL,
    completed_at        TEXT,
    summary_json        TEXT,               -- counts of discovered, modified, missing, unchanged

    FOREIGN KEY (scan_root_id) REFERENCES scan_root(id) ON DELETE RESTRICT,
    CHECK (status IN ('running', 'completed', 'failed', 'cancelled', 'partial'))
);

-- 7. Finding (unclassified or candidate filesystem object)
CREATE TABLE IF NOT EXISTS finding (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id         INTEGER NOT NULL,
    scan_root_id        INTEGER NOT NULL,
    rel_path            TEXT NOT NULL,
    filename            TEXT NOT NULL,
    state               TEXT NOT NULL DEFAULT 'current', -- 'current', 'missing', 'classified'
    classification      TEXT,               -- e.g. 'unsupported_format', 'corrupt', 'candidate'
    classified_file_id  INTEGER,            -- set if later promoted to File
    evidence_json       TEXT,
    discovered_at       TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (scan_run_id) REFERENCES scan_run(id) ON DELETE RESTRICT,
    FOREIGN KEY (scan_root_id) REFERENCES scan_root(id) ON DELETE RESTRICT,
    FOREIGN KEY (classified_file_id) REFERENCES file(id) ON DELETE RESTRICT,
    CHECK (state IN ('current', 'missing', 'classified'))
);

-- 8. ScanEvent (append-only audit log)
CREATE TABLE IF NOT EXISTS scan_event (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id         INTEGER NOT NULL,
    event_type          TEXT NOT NULL,      -- 'file_discovered', 'file_modified', 'file_missing', 'error', etc.
    entity_type         TEXT,               -- 'file', 'photo', 'finding', 'scan_root'
    entity_id           INTEGER,
    rel_path            TEXT,
    occurred_at         TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details_json        TEXT,

    FOREIGN KEY (scan_run_id) REFERENCES scan_run(id) ON DELETE RESTRICT
);

-- Indexes for efficient Inspector and Scanner navigation
CREATE INDEX IF NOT EXISTS idx_file_photo ON file(photo_id);
CREATE INDEX IF NOT EXISTS idx_file_root ON file(scan_root_id);
CREATE INDEX IF NOT EXISTS idx_file_version_file ON file_version(file_id);
CREATE INDEX IF NOT EXISTS idx_file_version_sha256 ON file_version(sha256);
CREATE INDEX IF NOT EXISTS idx_photo_derivation_derived ON photo_derivation(derived_photo_id);
CREATE INDEX IF NOT EXISTS idx_photo_derivation_source ON photo_derivation(source_photo_id);
CREATE INDEX IF NOT EXISTS idx_scan_run_root ON scan_run(scan_root_id);
CREATE INDEX IF NOT EXISTS idx_finding_root ON finding(scan_root_id);
CREATE INDEX IF NOT EXISTS idx_finding_run ON finding(scan_run_id);
CREATE INDEX IF NOT EXISTS idx_scan_event_run ON scan_event(scan_run_id);
CREATE INDEX IF NOT EXISTS idx_scan_event_type ON scan_event(event_type);
```

---

## 3. Consequences

### Positive
- **Exact alignment with frozen conceptual model:** Replaces temporary Phase 1 tables with the exact entities specified in `docs/data-model.md`.
- **Relational Integrity:** Foreign keys enforce valid entity graphs (`Photo` $\leftarrow$ `File` $\leftarrow$ `FileVersion`).
- **Auditability:** `scan_event` provides a reliable append-only record of scanner decisions.
- **Independence of Logical Photo:** Multiple physical files (copies, RAW+JPEG) map cleanly to one logical Photo without data duplication or artificial primary key constraints on SHA-256.

### Migration & Compatibility
- Existing Phase 1 test databases can be migrated or regenerated cleanly using deterministic test scripts (see `docs/test-scenarios.md`).
- The Data Inspector UI in Phase 2B can implement endpoints querying these tables directly.
