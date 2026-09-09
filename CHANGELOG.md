# Changelog

All notable changes to Bilder are documented here.

Bilder is currently in early development. The changelog may therefore contain development milestones in addition to formal releases.

## Unreleased

### Architecture

- Transitioning Bilder from the previous photo-analysis and folder-summary implementation to a new self-hosted, database-backed photo management system.
- Defining the NAS as the canonical photo archive.
- Defining a stable logical Photo ID separate from file hashes.
- Defining SHA-256 as an exact file-version identifier.
- Planning perceptual hashing for visual similarity and duplicate detection.
- Defining external locations as sources containing copies or versions of photographs.
- Designing a reversible and auditable workflow for destructive operations.
- Planning a macOS bridge using Apple PhotoKit for Apple Photos and iCloud Photos integration.

### Repository

- Previous implementation moved to `archive/`.
- New architecture documentation is being established under `docs/`.

## v26.02

### Previous system

Last release of the previous Bilder implementation.

This release contained the existing folder-summary/statistics tooling.

The previous implementation is preserved under `archive/` for historical reference.

---

## Versioning

Bilder uses a calendar-based version format:

```text
vYY.MM
```

where:

- `YY` is the two-digit year
- `MM` is the two-digit month

For example:

```text
v26.02
v26.09
v27.01
```

A version number represents a project milestone or release date. It does not necessarily imply semantic-versioning-style breaking changes.

During early development, changes may remain under `Unreleased` until there is a meaningful milestone worth tagging.