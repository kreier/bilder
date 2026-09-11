# Bilder — Data Model

## Status

**Phase 2A data model frozen — 2026-09-11**

This document defines the conceptual data model. It is intentionally independent of the exact SQLite schema.

The database schema must be derived from these concepts rather than allowing incidental table structure to redefine them.

## 1. Core entities

### Photo

A logical photograph.

Properties include an opaque `photo_id`, lifecycle state, current effective metadata, and historical provenance.

A Photo can exist without a current File.

### File

A cataloged physical filesystem file.

Each File belongs to exactly one Photo.

A Photo may have many Files.

A File has an opaque `file_id` and mutable filesystem attributes such as current path.

### FileVersion

A historical observed state of a File.

A File can have multiple FileVersions.

Each version records the byte identity using SHA-256 and relevant observed technical metadata.

### ScanRoot

A configured filesystem location to scan.

Each root has a stable opaque `root_id`, a current path, configuration history, and scan history.

### ScanRun

One scanner execution.

It records scope, configuration/software context, timestamps, status, and summary information.

### ScanEvent

A meaningful historical scanner outcome.

Events are append-only and associated with a ScanRun. They can describe discovery, unchanged state, new files, modifications, moves, missing/deleted observations, exclusions, invalid formats, failures, and root-level outcomes.

### Finding

A potentially relevant filesystem object that has not yet been confidently classified as a cataloged File.

A Finding has persistent identity and historical classification state.

A Finding may later become associated with a File. The Finding remains as provenance.

### PhotoDerivation

A directional provenance relationship between Photos.

It records that one Photo was derived from one or more source Photos.

The relationship can eventually carry a transformation type and evidence.

## 2. Core relationships

```text
Photo 1 ────< File 1 ────< FileVersion
```

```text
Photo >──── PhotoDerivation ────< Photo
```

```text
ScanRoot 1 ────< ScanRun
ScanRun  1 ────< ScanEvent
```

Findings are deliberately outside the File hierarchy until classification.

## 3. Identity invariants

### Photo identity

Photo identity does not depend on:

- path
- filename
- hash
- dimensions
- metadata
- physical storage location

### File identity

A File normally survives:

- rename
- move
- metadata changes
- content changes

Content changes create a new FileVersion.

A copied physical file receives a separate File identity.

### FileVersion identity

A FileVersion represents a particular observed content state.

SHA-256 is authoritative for exact bytes.

SHA-256 is not unique as a logical Photo identifier and is not constrained to one Photo globally.

If identical bytes are associated with conflicting Photo identities, the conflict is reviewable rather than automatically merged.

## 4. Lifecycle

### Photo

Normal conceptual states:

```text
active ↔ missing
```

`missing` means that no current cataloged File is associated with the Photo.

The Photo and its history remain available.

Explicit purge is a separate future operation.

### File

A File may move through states such as:

```text
present
missing
excluded
```

The precise operational state machine belongs to the SQLite implementation.

Historical versions and events are retained.

### Finding

A Finding may be:

```text
current
missing
classified
reclassified
```

The exact state representation is implementation-specific.

Classification into a File does not erase the Finding.

## 5. Identity evidence

Identity matching uses progressively stronger evidence.

Examples include:

- known path/history
- SHA-256
- file metadata
- filename and pairing signals
- deterministic visual evidence later

No single weak similarity signal may silently merge Photos.

Automatic classification should distinguish:

```text
certain       → automatic association
uncertain     → review/proposal
different     → separate identity
```

Human decisions are recorded and reversible.

## 6. Metadata model

Metadata has two conceptual layers:

### Observations

What a source actually reported.

Examples:

- EXIF capture time
- GPS
- camera make/model
- lens
- filesystem timestamps
- XMP values

### Effective catalog values

Bilder's current interpretation.

Precedence is conceptually:

```text
manual/catalog
      ↓
extracted
      ↓
no value
```

AI/inferred values are proposals unless accepted according to the future review/acceptance workflow.

Every inferred or competing value retains provenance and, where appropriate, confidence and evidence.

## 7. History

Historical information should answer:

- When was this file discovered?
- Where was it found?
- Which scan found it?
- What bytes were observed?
- What metadata was observed?
- What changed?
- Which Photo was it associated with?
- Why was that association made?
- What did a user decide?
- Was a decision later reversed?

Historical facts are not silently replaced by the latest observation.

## 8. Unassociated findings

Only potentially relevant filesystem objects need to become Findings.

Ordinary unrelated files may simply be ignored by the scanner.

A Finding may be retained even when the physical object disappears.

If it reappears, the scanner may restore the existing Finding identity using appropriate evidence.

When classified as a File:

```text
Finding #42
     │
     └── classification ──> File #501 ──> Photo #123
```

The Finding remains historical provenance.

## 9. Derivation

A derived Photo is a new logical Photo.

Examples:

- crop
- substantial resize
- major retouch
- object removal
- composite
- artistic transformation

A derived Photo may have multiple parents.

The provenance graph may therefore be:

```text
Photo A ─┐
         ├──> Photo C ───> Photo D
Photo B ─┘
```

The original Photo does not need to remain physically present for the provenance relationship to be historically meaningful.

Exactly how purge affects such a graph is deferred to the future purge design.

## 10. Conceptual entity checklist

### Core

- Photo
- File
- FileVersion
- PhotoDerivation

### Discovery

- ScanRoot
- ScanRun
- ScanEvent
- Finding

### Metadata

- metadata observations
- effective metadata
- metadata provenance/evidence

### Future

- tags
- collections
- saved searches
- face observations/clusters/persons
- proposals/decisions/operations
- visual fingerprints
- external source integrations

These future concepts must not be allowed to complicate the core Phase 2 scanner model prematurely.

## 11. Schema implementation principle

The conceptual model comes first:

```text
Concepts
   ↓
Relationships
   ↓
State transitions
   ↓
SQLite schema
   ↓
Migrations
   ↓
Services
   ↓
API
   ↓
UI
```

The Database Inspector should be built early enough to validate the resulting SQLite representation against these conceptual invariants.