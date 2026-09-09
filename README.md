# Bilder

Bilder is a self-hosted photo archive and management system designed to organize, catalog, preserve, and manage a large personal photo collection.

The long-term goal is to provide a single, searchable catalog of photographs while keeping the original files under the user's control on a NAS.

## Status

**Early development — architecture and design phase**

The current repository is being transitioned from an older collection of photo-analysis and folder-summary tools to a new database-backed photo management system.

The previous implementation has been moved to [`archive/`](archive/) for historical reference. It is no longer the active system.

No production system or public release of the new application exists yet.

## Goals

The new Bilder system is intended to:

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

This architecture is a design target. Components will be introduced incrementally rather than implemented all at once.

## Photo identity

Bilder deliberately separates several concepts of identity.

### Photo ID

Every logical photograph will have a stable internal `photo_id`.

This identifies the photograph as a logical entity and does **not** identify a particular file.

### File version

Every physical file is a file version.

A file version can be identified by its SHA-256 hash, together with other information such as size and provenance.

Changing metadata or otherwise modifying a file may therefore create a new file version with a different SHA-256 hash while remaining associated with the same logical `photo_id`.

### Visual identity

Perceptual hashes such as pHash may be used to identify visually similar files, including resized, recompressed, or edited versions.

These identities serve different purposes and must not be conflated.

## External sources

External locations such as:

- Apple Photos / iCloud Photos
- Google Drive
- phone backups
- camera or SD cards
- other filesystem locations

will be treated as sources containing copies or versions of photographs.

The NAS is intended to remain the canonical archive.

An external copy being identified as a duplicate does not automatically mean that it will be deleted.

## Safety

Bilder is designed around the principle that potentially destructive operations must be explicit and traceable.

The intended workflow is:

```text
discover
   ↓
compare
   ↓
recommend
   ↓
user approval
   ↓
quarantine
   ↓
verify
   ↓
optional permanent deletion
```

The system should never silently delete photographs merely because they appear to be duplicates.

## Development approach

Development will proceed in small, independently testable steps.

The planned progression is approximately:

1. Architecture and documentation
2. Database schema
3. Read-only filesystem scanner
4. File hashes and metadata catalog
5. Thumbnail generation
6. Basic web interface
7. Duplicate detection
8. Safe file operations and quarantine
9. macOS bridge
10. Apple Photos / iCloud integration
11. Google Drive integration

The order may change as development progresses.

## Historical implementation

The previous Bilder implementation contained scripts and tools for working with photo collections, including Google Photos, iCloud exports, NAS data, and folder statistics.

That implementation is preserved under [`archive/`](archive/) but is no longer the basis of the new system.

The last release of the previous system was `v26.02`.

## Repository structure

The repository is intentionally being developed incrementally.

```text
Bilder/
├── archive/          # Previous implementation
├── docs/             # Architecture and development documentation
├── README.md
├── AGENTS.md
├── CHANGELOG.md
├── SECURITY.md
└── CONTRIBUTING.md
```

Additional application directories will be introduced when the corresponding implementation work begins.

## License

License information will be added when the project's distribution model has been decided.