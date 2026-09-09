# AGENTS.md

Instructions for AI coding agents working on the Bilder repository.

## Project status

Bilder is in early development.

The repository is transitioning from an older photo-management implementation to a new self-hosted, database-backed system.

The old implementation is stored under `archive/` and should be treated as historical code unless a task explicitly concerns the archived implementation.

Do not assume that the new application architecture has already been implemented.

## Development philosophy

Develop Bilder incrementally.

Prefer:

- small changes
- understandable commits
- independently testable components
- explicit design decisions
- documentation before implementation when architecture is uncertain
- reversible operations
- minimal dependencies

Do not generate the entire planned application architecture merely because it appears in the documentation.

Implement only the component required for the current task.

## Planned architecture

The intended architecture consists of:

- Raspberry Pi server
- Python/FastAPI backend
- SQLite database
- background workers
- NAS-based canonical photo storage
- browser-based frontend
- macOS bridge written in Swift
- Apple PhotoKit integration through the macOS bridge

These are architectural goals, not necessarily existing components.

## Photo identity

Never use SHA-256 as the logical photo identifier.

The intended model is:

- `photo_id` — stable identity of a logical photograph
- `file_version_id` — identity of a particular stored file version
- SHA-256 — exact content identity of a file version
- pHash or similar — visual similarity
- source identifier — identity assigned by an external system

Changing metadata may change a file's SHA-256 without changing its `photo_id`.

## Storage

The NAS is intended to be the canonical archive.

Do not assume that files found in external sources are canonical merely because they exist there.

External sources may contain:

- duplicates
- resized copies
- recompressed copies
- edited versions
- metadata variants
- files that do not exist in the canonical archive

## Destructive operations

Never implement automatic permanent deletion of photographs.

Potentially destructive operations must follow the conceptual workflow:

1. Discover
2. Compare
3. Recommend
4. Obtain explicit user approval
5. Quarantine
6. Verify
7. Permanently delete only as an explicit later action

A duplicate detection result is a recommendation, not permission to delete.

When implementing file operations, preserve an operation record containing enough information to understand what happened.

## Database

The real photo database is private.

Never commit:

- `photos.db`
- SQLite databases containing personal photo information
- database exports containing personal metadata
- real photo records
- real filenames or paths
- GPS coordinates
- iCloud identifiers
- Google Drive identifiers
- source-specific private identifiers

Schema definitions and migrations may be committed.

## Secrets

Never commit:

- passwords
- API keys
- access tokens
- private keys
- cookies
- authentication headers
- real `.env` files
- private network credentials

Use placeholders in examples.

The repository may contain an `.env.example`, but it must never contain real credentials.

## Privacy

Treat photo metadata as private data.

Do not expose or commit:

- filenames
- directory paths
- GPS coordinates
- timestamps tied to identifiable personal photographs
- personal names extracted from metadata
- cloud asset identifiers
- account identifiers
- private URLs

Public aggregate statistics may be generated if they cannot reasonably reveal individual photographs or personal information.

## iCloud / Apple Photos

The Raspberry Pi should not attempt to implement Apple's private iCloud Photos protocols.

The intended integration is:

```text
Bilder Server
      ↕
macOS Bilder Bridge
      ↕
Apple PhotoKit
      ↕
Photos / iCloud Photos
```

PhotoKit operations belong in the macOS bridge.

## Filesystem safety

Never modify a user's photo collection during development unless the task explicitly requires it and the operation is designed and documented for that purpose.

Prefer:

- read-only scanning
- dry runs
- test directories
- temporary files
- explicit confirmation
- verification after writes

over direct modification of the canonical archive.

## Public repository

This repository is public.

Before committing a change, consider whether it could reveal private information.

When uncertain, do not commit the data. Create a sanitized example instead.

## Documentation

Architecture decisions should be documented in `docs/`.

Significant architectural decisions should use an Architecture Decision Record under:

```text
docs/decisions/
```

Do not silently change an architectural assumption that is already documented.

## Testing

Tests should be safe to run without access to the real photo archive.

Use:

- fixtures
- generated test images
- temporary directories
- test databases
- mock source data

Do not make the test suite depend on the user's real NAS or personal cloud accounts.

## Git workflow

Keep commits focused.

A commit should ideally represent one logical change.

Avoid combining:

- refactoring
- new functionality
- unrelated formatting
- large generated files

in a single commit.

Do not rewrite history or force-push unless explicitly requested.

## When uncertain

If a task would require making a significant architectural assumption, document the assumption or ask before implementing it.

Do not invent infrastructure, credentials, paths, APIs, or external service behavior.