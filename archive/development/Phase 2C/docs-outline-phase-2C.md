# Bilder — Phase 2C Outline: Deterministic Catalog/Scanner

**Status:** Planned  
**Phase:** 2C  
**Prerequisite:** Phase 2A frozen; Phase 2B Data Inspector operational

## 1. Purpose

Phase 2C implements the deterministic filesystem-to-catalog pipeline.

Its purpose is to turn filesystem observations into the SQLite catalog according to the rules established in Phase 2A.

The scanner should be:

- deterministic,
- incremental,
- non-destructive,
- auditable,
- reproducible,
- safe against incomplete scans,
- and inspectable through the Phase 2B Data Inspector.

---

## 2. Fundamental pipeline

The conceptual pipeline is:

```text
Filesystem
    ↓
Discovery
    ↓
Candidate classification
    ↓
File observation
    ↓
Content / metadata extraction
    ↓
Identity matching
    ↓
Catalog update
    ↓
Audit events
    ↓
SQLite
    ↓
Data Inspector
```

The important architectural principle is:

> **Deterministic processing comes before probabilistic intelligence.**

Phase 2C should not depend on an LLM to perform basic cataloging.

---

## 3. Phase 2C boundaries

Phase 2C should establish the reliable deterministic foundation for later phases.

It should handle:

- filesystem discovery,
- supported-file detection,
- exclusion rules,
- scan-root handling,
- file identity,
- FileVersions,
- SHA-256,
- basic metadata extraction,
- Findings,
- scan history,
- missing detection,
- configuration snapshots,
- and audit events.

More sophisticated identity analysis can be added later.

---

## 4. Scanner architecture

### 4.1 Scan orchestration

Implement the ScanRun lifecycle:

```text
requested
    ↓
running
    ↓
successful / partial / cancelled / failed
```

Support:

- scan ownership,
- heartbeat,
- cancellation,
- recovery of abandoned scans,
- per-root results,
- final completion.

### 4.2 Root handling

For each selected ScanRoot:

1. Load effective configuration.
2. Record the configuration snapshot.
3. Validate root availability.
4. Discover filesystem objects.
5. Process candidates.
6. Record root result.
7. Only perform missing detection after successful observation.

---

## 5. Deterministic discovery

Discovery should produce a deterministic sequence of filesystem objects.

Apply:

- recursive traversal,
- supported-extension rules,
- exclusion patterns,
- hidden/system-file policy,
- symlink policy,
- candidate-file rules.

Discovery should not yet attempt sophisticated visual interpretation.

The output is an ordered set of filesystem observations ready for processing.

---

## 6. Candidate classification

For each potentially relevant object:

1. Determine whether it is a supported catalog candidate.
2. Verify the actual file type where required.
3. Ignore clearly irrelevant files.
4. Create or update a Finding when an object is potentially relevant but cannot yet be classified normally.

The scanner should preserve uncertainty rather than silently inventing a classification.

---

## 7. File matching

For a previously known filesystem object, matching should proceed from cheap/strong evidence toward more expensive analysis.

Conceptually:

```text
Known path
    ↓
path + size + mtime fast path
    ↓
known historical identity
    ↓
SHA-256
    ↓
additional deterministic evidence
    ↓
uncertain → review
```

Path is useful evidence but never sufficient by itself after a possible replacement.

---

## 8. FileVersion creation

When the physical contents of a tracked File change:

1. Preserve the existing File identity where appropriate.
2. Create a new FileVersion.
3. Calculate/store SHA-256.
4. Extract technical metadata.
5. Associate the version with the appropriate Photo.
6. Record the relevant audit event.

The previous FileVersion remains historical.

---

## 9. Photo association

Phase 2C should implement the deterministic portion of Photo association.

Strong evidence can automatically associate a File with an existing Photo.

Examples:

- known File identity,
- known Photo relationship,
- exact duplicate content,
- deterministic RAW/JPEG pairing where sufficiently strong,
- known historical relationships.

Ambiguous identity should remain unresolved rather than being forced.

Advanced visual identity analysis can be introduced later.

---

## 10. Metadata extraction

Extract deterministic technical metadata available from the file.

Potential examples include:

- dimensions,
- file type,
- file size,
- timestamps,
- camera information,
- lens information,
- exposure information,
- GPS,
- orientation,
- embedded metadata.

Store observations with provenance.

Do not automatically rewrite source files.

---

## 11. Findings

Implement the Finding lifecycle established in Phase 2A:

```text
discovered
    ↓
unassociated
    ↓
classified
    ↓
normal File
```

while retaining historical classification information.

Support:

- persistent Findings,
- disappearance,
- reappearance,
- deterministic matching,
- classification,
- reversal.

Detailed Finding versioning should follow the schema decisions made during implementation rather than expanding Phase 2C unnecessarily.

---

## 12. Missing detection

Missing detection must be conservative.

After a root scan completes successfully:

1. Determine which previously known objects belong to that root.
2. Determine which were observed.
3. Mark genuinely unobserved objects as missing.
4. Preserve their historical state.

If the root is:

- unavailable,
- cancelled,
- partially processed,
- or otherwise incomplete,

do **not** perform missing detection for the affected scope.

---

## 13. Transactions and recovery

Implement transactional boundaries so that:

- individual file processing can commit incrementally,
- crashes do not corrupt the catalog,
- completed work remains available after restart,
- final scan completion is atomic,
- missing detection only occurs after successful completion.

Abandoned ScanRuns must be identifiable and recoverable.

---

## 14. Audit events

Every meaningful catalog transition should produce an appropriate audit event.

Examples:

- File discovered,
- File moved,
- File changed,
- File disappeared,
- File reappeared,
- FileVersion created,
- Finding created,
- Finding classified,
- Photo associated,
- Photo became missing,
- root unavailable,
- scan completed,
- scan cancelled,
- scan failed.

Avoid recording every internal implementation operation.

The event stream should explain **what happened**, not expose every function call.

---

## 15. Configuration and reproducibility

Each scan must record enough configuration information to explain its behavior.

At minimum:

- selected roots,
- root paths,
- exclusions,
- supported extensions,
- recursive setting,
- symlink policy,
- candidate-file configuration,
- configuration versions,
- configuration hashes.

Use canonical configuration snapshots.

---

## 16. Incremental operation

The scanner should be designed for repeated execution.

A second scan of an unchanged filesystem should do substantially less work than the first scan.

The expected progression is:

```text
First scan
  → discover + hash + extract

Later scan
  → recognize unchanged files
  → skip unnecessary work
  → process only changes
```

Optimization should never compromise the authoritative identity/history rules.

---

## 17. Parallel processing

Parallel file processing may be introduced where useful.

The observable catalog result must remain deterministic.

In particular:

- discovery order is deterministic,
- event ordering is deterministic,
- database transactions do not depend on worker completion order.

Exact worker/resource configuration should be determined empirically rather than frozen prematurely.

---

## 18. Testing strategy

Phase 2C should be developed against small deterministic test datasets before being used on the user's real photo collection.

Tests should cover at least:

### Initial discovery

- new Photo
- new File
- multiple Files for one Photo
- unsupported file
- Finding

### File changes

- unchanged file
- metadata-only byte change
- content change
- in-place replacement
- new FileVersion

### Filesystem changes

- rename
- move
- copy
- deletion
- reappearance

### Identity

- exact duplicate
- RAW/JPEG pairing
- conflicting identity evidence
- ambiguous identity

### Roots

- successful root
- empty root
- unavailable root
- excluded path
- disabled root
- cancelled scan

### Recovery

- scanner interruption
- abandoned ScanRun
- restart during scan

### Reproducibility

- same filesystem + same configuration
- changed configuration
- changed exclusions
- changed supported extensions

---

## 19. Validation through Phase 2B

The Data Inspector should be used continuously during 2C.

After each important scanner feature:

```text
Test filesystem
      ↓
Run scanner
      ↓
Inspect SQLite through Data Inspector
      ↓
Verify expected state/history/events
```

This makes the Inspector part of the development feedback loop without making it part of the scanner itself.

---

## 20. Real-data rollout

Only after the deterministic scanner passes the synthetic test suite should it be tested against a controlled subset of the real photo collection.

Suggested progression:

```text
Synthetic fixtures
      ↓
Small real test directory
      ↓
Read-only scan of larger subset
      ↓
Full catalog scan
```

The first real-data runs should be treated primarily as validation rather than optimization.

---

## 21. Explicitly out of scope

Phase 2C should not yet attempt to solve:

- sophisticated perceptual identity,
- AI-based metadata inference,
- semantic image understanding,
- face recognition,
- natural-language search,
- automatic artistic/edit classification,
- final user-facing photo management,
- automatic source-file editing,
- advanced deduplication beyond deterministic evidence.

These belong to later phases once the deterministic catalog is trustworthy.

---

## 22. Completion criterion

Phase 2C is complete when the system can reliably perform repeated deterministic scans and maintain a correct, auditable catalog without requiring AI.

At minimum:

> **Given a filesystem and a recorded configuration, the scanner can deterministically discover relevant objects, maintain File/FileVersion/Photo/ Finding state, detect legitimate changes and disappearance, preserve history, and explain its actions through the audit trail.**

The Data Inspector must make these results inspectable.

---

## 23. Resulting Phase 2 sequence

```text
2A — Architecture & Data Model
        │
        │ freeze
        ▼
2B — Data Inspector
        │
        │ validate model
        ▼
2C — Deterministic Catalog/Scanner
        │
        │ establish trustworthy catalog
        ▼
Later phases
        │
        ├── advanced identity analysis
        ├── metadata intelligence
        ├── AI suggestions
        ├── search
        └── user-facing application
```

The central philosophy of Phase 2 is therefore:

> **First decide what the catalog means.  
> Then make the catalog observable.  
> Then build the deterministic machinery that populates it.**