# Bilder — Phase 2A Decision Log

**Status:** Archived  
**Phase:** 2A — Architecture and Data Model  
**Decision date:** 2026-09-11  
**Purpose:** Historical record of the architectural decisions that led to the Phase 2A freeze.

> **Important:** This document records the reasoning and decisions made during the Phase 2A design discussion. It is not the current implementation contract. For the current architecture, data model, and configuration rules, see `docs/architecture.md`, `docs/data-model.md`, and `docs/configuration.md`.

---

## 1. Purpose of the discussion

Phase 2A was used to establish the conceptual model and identify architectural decisions that would be expensive or difficult to change later.

The discussion deliberately started with a large number of detailed questions. Many of these were subsequently consolidated because they represented implementation details rather than genuine architectural decisions.

The final result was a deliberately smaller set of architectural principles.

---

## 2. Core identity model

### Decision

The catalog distinguishes four fundamentally different concepts:

- **Photo** — the logical photograph.
- **File** — a physical/cataloged filesystem representation of a photograph.
- **FileVersion** — a historical state of a physical file.
- **Finding** — a potentially relevant filesystem object that has not yet been classified as a normal cataloged File.

The central relationship is:

```text
Photo 1 ────< File 1 ────< FileVersion
```

A Photo may therefore have:

- multiple Files,
- multiple representations such as RAW and JPEG,
- duplicate physical copies,
- or temporarily no existing File.

A normal cataloged File always belongs to one Photo.

Potentially relevant objects that cannot yet be classified as Photos/Files are stored separately as Findings rather than as orphan Files.

---

## 3. Photo identity

Photo identity is **logical**, not physical.

A Photo is not identified by:

- filename,
- filesystem path,
- file size,
- modification time,
- SHA-256 hash,
- EXIF metadata,
- camera,
- or any other single physical property.

Photo IDs are opaque identifiers.

### Same Photo

The following normally remain the same Photo:

- moving or renaming a file,
- changing EXIF metadata,
- changing GPS information,
- changing title/rating information,
- changing EXIF orientation,
- technically rotating an image,
- minor color/exposure/contrast correction,
- sharpening,
- noise reduction,
- similar non-substantive corrections,
- different encodings of the same photograph,
- RAW/JPEG representations of the same photograph.

### New Photo

The following normally create a derived/new Photo:

- cropping,
- deliberate/substantive resizing,
- major retouching,
- object removal,
- compositing,
- background replacement,
- strong artistic transformation.

These rules are intentionally conservative. There is no attempt to define an absolute mathematical concept of "the same photograph."

Ambiguous cases must remain reviewable rather than being forced into an automatic decision.

---

## 4. Files and file versions

A physical file has its own opaque `file_id`.

Moving or renaming a tracked file does **not** create a new File.

If a file at the same path is replaced with different contents, the File can remain the same physical-file history while acquiring a new FileVersion.

Conceptually:

```text
File A
 ├── Version 1 → Photo 123 → SHA-256 A
 └── Version 2 → Photo 456 → SHA-256 B
```

This allows the catalog to preserve the history of an in-place replacement without pretending that the two physical contents are the same Photo.

Metadata changes that modify file bytes, such as writing GPS information into EXIF, therefore create a new FileVersion while normally remaining associated with the same Photo.

---

## 5. Duplicate physical files

Identical physical files are still separate File records.

For example:

```text
Photo 123
 ├── File 10 → /photos/2024/image.jpg
 └── File 27 → /backup/2024/image.jpg
```

SHA-256 is authoritative evidence of identical physical bytes.

However:

> **SHA-256 is not Photo identity.**

If the same SHA-256 appears under different Photo IDs, the catalog must not silently merge them. Such a situation is treated as a conflict requiring review.

There is no separate mandatory "duplicate relationship" at this stage; exact duplicates can be derived from their shared hash.

---

## 6. Moving, copying, deleting and replacing files

### Move or rename

A move or rename should preserve the existing File and Photo identities whenever the file can be confidently matched.

### Copy

A copied physical file is a separate File even when its contents are identical.

Both Files may point to the same Photo.

### Delete

Deleting a physical file does not delete its Photo history.

If other Files still represent the Photo, the Photo remains active.

If all Files disappear, the Photo becomes logically missing while its history remains in the database.

### Reappearance

A returning physical file should restore its existing File identity when it can be confidently identified.

A returning Photo should likewise restore its existing Photo identity when the evidence is sufficient.

---

## 7. Identity confidence

Identity decisions use evidence rather than a single universal rule.

The conceptual outcomes are:

- **certain** — sufficient evidence for automatic association,
- **uncertain** — plausible association, but requires review,
- **different** — evidence indicates a separate Photo.

Visual similarity alone is never sufficient for automatic merging.

Potential evidence includes:

- exact content hash,
- known path/history,
- metadata,
- dimensions,
- normalized image comparison,
- perceptual fingerprints,
- RAW/JPEG pairing,
- derivation information,
- other deterministic relationships.

The exact implementation of advanced visual identity analysis is intentionally deferred.

Manual identity decisions must be recorded and reversible.

---

## 8. Derivations and provenance

Derived Photos have an explicit provenance relationship to their source Photos.

Derivations may form chains:

```text
Original
   ↓
Crop
   ↓
Edited version
   ↓
Further derivative
```

A derived Photo may itself have multiple Files.

Multiple source Photos may also contribute to one derived Photo, for example in compositing.

Deletion of an original physical file does not remove the provenance relationship.

Normal deletion therefore never destroys historical provenance.

---

## 9. Findings

Not every potentially relevant filesystem object is immediately a cataloged File.

The scanner may discover an object that appears relevant but cannot yet be confidently classified.

Such an object becomes a **Finding**.

Examples might include:

- an unknown image format,
- a file with an unexpected extension,
- a potentially supported file whose contents cannot yet be classified,
- another filesystem object that may later prove relevant.

Ordinary unrelated files do not need to become Findings.

Findings are persistent historical objects.

If the underlying object disappears, the Finding remains in the database with an appropriate missing state.

If it later reappears, the same Finding should be restored when it can be confidently matched.

A Finding may later be classified as a normal File. The original Finding and classification history remain available.

Classification is reversible.

The exact versioning and metadata schema for Findings was intentionally not frozen during Phase 2A.

---

## 10. Scanning model

Scanning is treated as an **observation of the filesystem**, not as a destructive synchronization operation.

The catalog must therefore be able to distinguish:

- file discovered,
- file changed,
- file moved,
- file renamed,
- file disappeared,
- root unavailable,
- scan cancelled,
- scan failed,
- and other meaningful outcomes.

### Scan roots

Multiple scan roots are supported.

Each root has persistent identity and history, including:

- path,
- configuration,
- label,
- enabled/disabled state,
- scan history.

Unavailable roots are preserved rather than being treated as empty directories.

Disabled roots are skipped and do not generate missing-file events.

---

## 11. Safe missing detection

Missing detection is only valid when the relevant filesystem scope was successfully observed.

If a scan is cancelled or a root is unavailable, the system must **not** conclude that files under that root have disappeared.

A complete scan therefore has a final completion step that establishes which parts of the filesystem were actually observed.

This prevents a temporary disk/network problem from turning into thousands of false deletions.

---

## 12. Scan runs and events

Every scan is represented by a persistent `scan_run_id`.

Scan runs record:

- selected scope,
- configuration snapshot,
- root results,
- status,
- timestamps,
- meaningful events,
- and enough information to understand what happened.

Events are append-only historical records.

Events have:

- actor,
- timestamp,
- sequence,
- reason/evidence,
- and structured canonical JSON payload where appropriate.

The system records meaningful outcomes rather than every internal implementation step.

Actors include concepts such as:

```text
scanner
manual
import
ai
system
```

### Scan status

Overall scan status:

```text
running
successful
partial
cancelled
failed
aborted
```

Root-level status:

```text
pending
running
successful
unavailable
failed
cancelled
skipped
```

Overall success requires all selected roots to complete successfully.

If one or more selected roots are unavailable or fail, the overall result is partial unless all selected roots fail, in which case the result is failed.

A scan with zero selected roots is a successful no-op.

---

## 13. Scan concurrency and recovery

Only one overall catalog scan run is allowed at a time.

Different roots may be processed concurrently within that scan.

A root must not be scanned concurrently by two independent scan operations.

Scans support cancellation.

A cancelled scan performs no missing-file detection.

The system records ownership and heartbeat information so that an abandoned scan can be detected and recovered after application restart.

The exact heartbeat timeout and worker/resource configuration were deliberately not frozen during Phase 2A.

---

## 14. Determinism

The scanner must produce deterministic results where practical.

In particular:

- filesystem discovery order is deterministic,
- configuration is explicitly recorded,
- scan scope is recorded,
- important decisions are auditable,
- event ordering is based on deterministic discovery order rather than thread completion order.

Parallel file processing is permitted as an implementation optimization, provided it does not make the catalog's observable history nondeterministic.

---

## 15. Hashing

SHA-256 is the authoritative content hash.

Hashing is performed during scanning when required.

A fast path may use:

```text
path + size + modification time
```

to avoid unnecessary re-reading of unchanged files.

Whether modification time may be trusted is configurable.

The hash algorithm itself is recorded so that the meaning of stored hashes remains explicit.

Fast fingerprints and more advanced optimization techniques were deferred.

---

## 16. Metadata and provenance

Metadata is treated as observations with provenance rather than as one undifferentiated value.

Potential sources include:

- extracted metadata,
- manually entered/catalog metadata,
- AI-generated suggestions.

Manual values take precedence over extracted values for the current effective value.

Conflicting extracted/manual values are not silently destroyed; the underlying observations remain available.

AI does not silently overwrite authoritative metadata.

Suggested or inferred values have:

- confidence,
- evidence,
- source,
- and rule/software/configuration context.

Confidence is represented as a value from `0.0` to `1.0`.

Confidence describes the likelihood that the candidate value is correct; it is distinct from the reliability of the source itself.

Automatic acceptance thresholds are configurable and may eventually be field-specific.

---

## 17. Reproducibility

Important scanner configuration is part of the reproducible catalog state.

Configuration snapshots use canonical JSON and have a SHA-256 configuration hash.

The configuration includes relevant properties such as:

- root path,
- exclusions,
- supported extensions,
- recursive behavior,
- symlink policy,
- candidate-file configuration,
- and other scanner behavior affecting discovery.

Presentation-only information such as a root label does not affect reproducibility identity.

The enabled/disabled operational state is likewise separate from the reproducibility configuration.

Configuration changes create new configuration versions when the effective behavior changes.

---

## 18. Source-file safety

The catalog never automatically modifies source files.

In particular:

- no automatic EXIF rewriting,
- no automatic sidecar creation,
- no automatic filename modification,
- no destructive normalization.

The database is the authoritative catalog.

Source files remain external objects observed by the catalog.

---

## 19. Database rebuild policy

Normal rescans preserve existing opaque Photo and File identities.

A complete database rebuild is allowed to generate new IDs.

No separate identity manifest is required at this stage solely to preserve IDs across a total rebuild.

If export/import or long-term identity preservation across complete rebuilds becomes a real requirement, it can be designed later.

---

## 20. Decisions deliberately deferred

The following topics were discussed but intentionally **not** frozen as Phase 2A architecture:

- exact SQLite column definitions,
- exact Finding version schema,
- detailed metadata table structure,
- exact confidence thresholds,
- fast fingerprints,
- worker counts,
- CPU/memory limits,
- detailed performance tuning,
- queue implementation,
- UI implementation details,
- AI/ML identity algorithms,
- advanced image comparison,
- storage/purge implementation,
- final user-facing Web UI,
- detailed authorization/security model.

These belong to implementation or later phases unless a concrete architectural conflict emerges.

---

## 21. Important discarded or consolidated questions

The original design discussion contained substantially more questions than the final architecture requires.

Several groups were deliberately consolidated:

### Performance and concurrency

Questions about exact worker counts, CPU limits, memory limits, queue sizes and similar tuning were recognized as implementation details.

They should not constrain the Phase 2 architecture prematurely.

### Finding internals

Questions about exact Finding version records, version identifiers and detailed metadata storage were stopped before becoming architecture commitments.

The architectural decision is simply that Findings are persistent, historical, reversible classification candidates.

### Identity edge cases

Rather than attempting to enumerate every possible image transformation, the architecture uses conservative identity principles:

> Preserve Photo identity for changes that do not materially change the photograph; create a derived Photo for transformations that materially change its visual content or composition.

Ambiguous cases remain reviewable.

---

## 22. Final Phase 2A principles

The long design discussion ultimately reduced to these twelve principles:

1. **Photo, File, FileVersion and Finding are distinct concepts.**
2. **Photo identity is logical; File identity represents physical-file history.**
3. **Paths and filenames are attributes, never identities.**
4. **A Photo may have multiple Files and may temporarily have none.**
5. **FileVersions preserve the history of physical file contents.**
6. **Transformations create either the same Photo or a derived Photo according to conservative identity rules.**
7. **Provenance is a first-class concept and human decisions are reversible.**
8. **SHA-256 establishes byte identity but does not define Photo identity.**
9. **The database is the authoritative catalog; source files are not modified automatically.**
10. **Scanning is deterministic, auditable, reproducible and safe against incomplete filesystem observations.**
11. **Potentially relevant but unclassified filesystem objects can persist as Findings.**
12. **Detailed schema, performance, UI and AI decisions are deferred until implementation and validation.**

---

## 23. Resulting development sequence

The Phase 2A discussion resulted in the following development sequence:

```text
Phase 2A
  │
  ├── Conceptual model
  ├── SQLite model
  ├── Scanner contract
  ├── Audit/reproducibility contract
  └── Architecture freeze
          │
          ▼
    Database Inspector
          │
          ▼
    Validate catalog model
          │
          ▼
Phase 2B
    Deterministic scanner/catalog implementation
          │
          ▼
Later phases
    Identity analysis
    Metadata intelligence
    AI suggestions
    User-facing Web UI
```

The **Database Inspector** was intentionally placed between the architecture freeze and Phase 2B. Its purpose is to provide a microscope into the actual SQLite state before the deterministic scanner becomes more sophisticated.

---

## 24. Source of truth

This file is an **archive of the design process**.

If this document ever differs from the current project documentation, the current documentation takes precedence:

- `docs/architecture.md`
- `docs/data-model.md`
- `docs/configuration.md`

The archived decision log exists so that future development can answer:

> "Why was the architecture designed this way?"

rather than requiring the original discussion to be reconstructed from conversation history.