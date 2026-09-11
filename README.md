# Bilder

Bilder is a self-hosted photo archive and management system designed to organize, catalog, preserve, and manage a large personal photo collection.

The long-term goal is to provide a single, searchable catalog of photographs while keeping the original files under the user's control on a NAS.

## Status

**Early development — Stage 2B: Data Inspector**

The repository has transitioned from historical scripts to a modern, database-backed photo management architecture:
- **Phase 1 (Completed):** Established initial groundwork, prototype SQLite schema, read-only scanner, and initial FastAPI / React dashboard.
- **Phase 2A (Completed):** Formally froze the architectural principles and conceptual data model ([`docs/architecture.md`](docs/architecture.md) and [`docs/data-model.md`](docs/data-model.md)).
- **Phase 2B (Current):** Developing the read-only **Data Inspector** to observe and validate the catalog model against synthetic test datasets before expanding scanner complexity ([`docs/phase-2b-inspector.md`](docs/phase-2b-inspector.md)).
- **Phase 2C (Next):** Full deterministic filesystem scanner and catalog pipeline.

The previous photo-analysis scripts have been moved to [`archive/`](archive/) for historical reference.

## Goals

The Bilder system is intended to:

- maintain a central catalog of photographs
- keep the NAS as the canonical storage location for originals
- preserve file history and provenance
- identify exact duplicate files
- identify visually similar photographs and different versions of the same photograph
- collect and preserve metadata such as EXIF information
- generate thumbnails for efficient browsing
- provide a web-based interface
- connect external photo sources such as Apple Photos/iCloud Photos and Google Drive
- distinguish canonical files from copies held by external sources
- provide safe, reversible workflows for potentially destructive operations
- maintain enough information in the files and metadata to assist recovery if the database is lost

## Planned architecture

The planned system consists of several components:

```text
                         ┌─────────────────┐
                         │     Browser     │
                         └────────┬────────┘
                                  │
                               HTTP/API
                                  │
                         ┌────────▼────────┐
                         │  Bilder Server  │
                         │  Raspberry Pi   │
                         ├─────────────────┤
                         │ FastAPI         │
                         │ SQLite          │
                         │ Workers         │
                         └───────┬─────────┘
                                 │
                 ┌───────────────┼────────────────┐
                 │               │                │
          ┌──────▼──────┐ ┌─────▼─────┐  ┌──────▼──────┐
          │     NAS     │ │ Thumbnails│  │   Sources   │
          │  Canonical  │ │           │  │   Catalog   │
          │   Library   │ │           │  │             │
          └─────────────┘ └───────────┘  └─────────────┘

                         ┌─────────────────┐
                         │   macOS Bridge  │
                         └────────┬────────┘
                                  │
                              PhotoKit
                                  │
                         ┌────────▼────────┐
                         │  Apple Photos   │
                         │  / iCloud       │
                         └─────────────────┘
```

This architecture is a design target. Components are introduced incrementally rather than implemented all at once.

## Core identity model

Bilder strictly separates logical identity from physical filesystem files:

```text
Photo 1 ────< File 1 ────< FileVersion
```

- **Photo (`photo_id`):** The logical photograph. Independent of filenames, paths, or hashes. Alternate representations (RAW + JPEG), moved files, and physical copies share the same logical Photo.
- **File (`file_id`):** A cataloged physical file at a specific tracked path. Moving or renaming a file preserves its File identity.
- **FileVersion (`file_version_id`):** An observed byte state of a File, identified by its authoritative SHA-256 hash, size, and timestamp. In-place content changes produce a new FileVersion under the same File.
- **Finding (`finding_id`):** An unclassified filesystem candidate object that has not yet been associated with a Photo or File.
- **PhotoDerivation:** Directional provenance tracking for crops, substantial edits, and multi-parent composite photos.

## External sources

External locations such as:

- Apple Photos / iCloud Photos
- Google Drive
- phone backups
- camera or SD cards
- other filesystem locations

are treated as sources containing copies or versions of photographs. The NAS remains the canonical archive. An external copy being identified as a duplicate does not automatically trigger deletion.

## Safety & non-destructive operations

Bilder is designed around the principle that potentially destructive operations must be explicit, reviewable, and traceable:

```text
discover ──> compare ──> recommend ──> user approval ──> quarantine ──> verify ──> optional permanent deletion
```

The scanner observes; it does not automatically move, rename, or delete files on disk.

## Development roadmap

Development follows the 6-stage roadmap defined in [`docs/current_plan.md`](docs/current_plan.md):

```text
Stage 1: Foundation / Initial groundwork (Completed)
   ↓
Stage 2: Deterministic Catalog (In progress)
   ├── 2A: Architecture & Data Model Freeze (Completed)
   ├── 2B: Data Inspector (Current)
   └── 2C: Deterministic Scanner & Pipeline (Next)
   ↓
Stage 3: Metadata & Provenance
   ↓
Stage 4: Preservation & Storage Management
   ↓
Stage 5: Search & Collection Management
   ↓
Stage 6: Probabilistic & AI Analysis
```

## Documentation

Key design specifications and decisions are maintained under `docs/`:

- **Architecture:** [`docs/architecture.md`](docs/architecture.md) — Frozen core principles and invariants.
- **Data Model:** [`docs/data-model.md`](docs/data-model.md) — Conceptual entity and relationship models.
- **Current Roadmap:** [`docs/current_plan.md`](docs/current_plan.md) — Stage-by-stage development sequence.
- **Data Inspector Specification:** [`docs/phase-2b-inspector.md`](docs/phase-2b-inspector.md) — Requirements and views for Stage 2B.
- **Architecture Decisions:** [`docs/decisions/`](docs/decisions/) — ADRs, including [ADR 0001: Phase 2 SQLite Schema](docs/decisions/0001-phase-2-schema.md).
- **Test Scenarios:** [`docs/test-scenarios.md`](docs/test-scenarios.md) — Synthetic test fixtures for validation.
- **Agent Instructions:** [`AGENTS.md`](AGENTS.md) — Development rules for AI coding assistants.

## Repository structure

```text
bilder/
├── archive/          # Historical scripts (v26.02 and earlier)
├── docs/             # Active architecture, specifications, and ADRs
│   └── decisions/    # Architecture Decision Records
├── frontend/         # React / TypeScript / Vite web interface
├── src/              # Python application package
│   └── bilder/       # Scanner, SQLite catalog, and FastAPI server
├── tests/            # Automated test suite
├── pyproject.toml    # Python project configuration and dependencies
├── AGENTS.md         # Guidelines for AI coding agents
├── CHANGELOG.md      # Project version changelog
├── LICENSE           # MIT License
└── README.md
```

## License

This project is licensed under the [MIT License](LICENSE).