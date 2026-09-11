# Bilder — Architecture

## Status

**Phase 2A architecture frozen — 2026-09-11**

This document is the implementation contract for the architecture established during Phase 2A.

It deliberately separates architectural commitments from implementation details. SQLite table layout, indexes, exact version structures, performance tuning, UI details, and AI algorithms may be decided during implementation without reopening the architectural model.

## 1. Architectural principles

1. **The catalog is non-destructive by default.** Discovering, scanning, or cataloging a file does not modify the source file.
2. **History is first-class.** Meaningful observations, state changes, decisions, and provenance are retained rather than silently overwritten.
3. **Identity is independent of paths.** Paths and filenames are attributes, not identities.
4. **Machine conclusions are evidence/proposals.** Human decisions are authoritative and reversible.
5. **Scanning is observation, not import.** Discovery does not itself imply preservation, deletion, or other filesystem changes.
6. **Determinism comes before optimization.** Discovery order and scanner outcomes must be reproducible; parallel processing must not make historical ordering nondeterministic.
7. **The database is the authoritative catalog.** Source files are not used as a hidden metadata database and are not automatically modified.

## 2. Core conceptual model

The core relationship is:

```text
Photo 1 ────< File 1 ────< FileVersion
```

A Photo may have zero, one, or many Files.

A File belongs to exactly one Photo.

A File may have multiple FileVersions over time.

Physical filesystem copies are represented independently as Files. Identical physical files may therefore have different `file_id` values while sharing a Photo.

Photo provenance is separate:

```text
Photo >──── PhotoDerivation ────< Photo
```

A derived Photo may have multiple source Photos.

Unassociated filesystem findings are separate from cataloged Files:

```text
Filesystem
   ├── File ───────> Photo
   └── Finding
```

A Finding can later be classified into a File, while its historical Finding record remains available.

## 3. Identity

### Photo

`photo_id` is an opaque logical identity for a photograph.

It is not derived from:

- filename
- filesystem path
- SHA-256
- capture date
- metadata

Renaming, moving, metadata changes, alternate representations, and physical copies do not inherently create a new Photo.

### File

`file_id` is an opaque identity for a cataloged physical file/history.

A move or rename normally preserves the File identity.

A physical copy is a separate File even when its bytes are identical.

An in-place change keeps the File identity but creates a new FileVersion.

### FileVersion

A FileVersion represents one observed byte-level state of a File.

SHA-256 is the authoritative exact-content hash.

A hash is evidence of byte identity; it is **not** logical Photo identity.

### Database rebuild

Normal rescans must preserve identities. A complete database rebuild is allowed to generate new opaque IDs. A future identity-manifest/import mechanism may be considered if a real requirement emerges.

## 4. Photo identity and transformations

The catalog uses conservative identity rules rather than attempting to define an absolute mathematical notion of photographic sameness.

Generally the same Photo may include:

- alternate encodings
- RAW + JPEG representations
- metadata changes
- EXIF orientation/rotation changes
- minor visual corrections

Substantive transformations generally create a new Photo, including:

- cropping
- substantial resizing
- major retouching
- object removal
- compositing
- major artistic transformation

Derived Photos retain explicit provenance.

Ambiguous automatic associations must be reviewable rather than being forced into an irreversible merge.

## 5. Scan roots and scanning

A ScanRoot has an opaque stable identity independent of its current filesystem path.

Root configuration includes reproducibility-relevant settings such as:

- filesystem path
- include/exclude patterns
- supported extensions
- recursive scanning
- symlink policy
- candidate-file configuration

Human-readable labels and enabled/disabled presentation state are not part of reproducibility configuration.

Scanning is:

- recursive by default
- case-insensitive for supported extensions
- non-following for symlinks by default
- deterministic in discovery order
- safe against incomplete roots

Hidden/system files are not automatically excluded.

An unavailable, failed, or incomplete root must not cause its existing cataloged files to be marked missing.

## 6. Scan runs and events

Every scanner execution has a persistent ScanRun.

The ScanRun records enough information to reproduce and audit the run, including:

- selected roots
- scanner/software version
- effective configuration snapshot and hash
- timestamps
- status
- summary
- errors

Root-level results distinguish successful, unavailable, failed, cancelled, skipped, and pending/running states.

Overall scan completion and missing-file detection are committed consistently. Cancellation or incomplete execution must not trigger global missing detection.

Meaningful file/root outcomes may be recorded as append-only ScanEvents with timestamps, deterministic sequence ordering, actor/source, and structured evidence.

## 7. Findings

The scanner may retain potentially relevant filesystem objects that cannot yet be confidently classified as cataloged photo Files.

Findings:

- have persistent identity
- survive rescans
- may become missing
- may reappear
- may later be classified as Files
- retain classification history
- support reversible manual classification

The original Finding remains historical provenance after classification.

The exact finding-version schema is an implementation detail and is intentionally not frozen here.

## 8. Metadata and provenance

Metadata has distinct provenance categories, including:

- extracted/embedded metadata
- catalog/manual metadata
- AI/inferred metadata
- other external sources

Manual/catalog values take precedence over extracted values for the current effective catalog value.

AI suggestions must not silently overwrite trusted values.

Inferred values may carry:

- confidence from 0.0 to 1.0
- structured evidence
- rule/algorithm version
- Bilder version
- configuration snapshot/hash

Historical evidence is immutable; new processing creates new observations rather than rewriting old evidence.

## 9. Missing and deletion semantics

A Photo may exist without a current File.

Normal deletion therefore produces a historical state such as:

```text
Photo → missing
File  → no current physical presence
history → retained
```

Normal deletion does not purge the logical identity or its history.

An explicit purge is a separate future storage-management operation. It is not part of normal lifecycle semantics and may be used only when retention/storage requirements justify it.

The future purge mechanism must account for provenance and surviving derived Photos, but this is intentionally deferred.

## 10. Human decisions and provenance

Automatic analysis produces evidence or proposals.

Human classification/identity decisions are durable historical information and must be reversible.

A decision must not silently disappear merely because a later algorithm produces a different result.

## 11. Deferred architecture

The following are deliberately **not** Phase 2A architecture decisions:

- exact SQLite schema
- exact table/column names where not required by the conceptual model
- indexes
- transaction sizing
- worker counts
- CPU/memory limits
- caching
- fast fingerprints
- perceptual-hash algorithms
- visual-similarity algorithms
- AI models/prompts
- exact confidence thresholds
- final Web UI
- purge implementation
- total database rebuild/identity-manifest mechanism

These should be decided when implementation and real catalog data provide useful evidence.

## 12. Development sequence

1. Phase 2A architecture freeze
2. Implement/update conceptual data model and SQLite schema
3. Build the **Database Inspector**
4. Validate the model against real database state
5. Implement Phase 2B deterministic catalog/scanner
6. Add deeper analysis and review workflows later

The Database Inspector is a developer/admin tool, not the final user-facing application UI. It should expose the database state without duplicating domain logic.