# Proposed development sequence

## Phase 1 — Foundation and model validation

**Completed**

1. `architecture.md` ✅
2. `data-model.md` ✅
3. Define implementation boundary ✅
4. Define initial SQLite schema ✅
5. Build initial scanner groundwork ✅
6. Test against representative files ✅
7. Resolve fundamental identity, provenance and scan-history decisions ✅

The result is the conceptual foundation:

```text
Photo
  └── File
        └── FileVersion

Finding
ScanRoot
ScanRun
Event
Metadata / provenance
```

The database is the authoritative catalogue, while the filesystem remains unchanged by the scanner.

---

# Phase 2 — Deterministic catalogue

Phase 2 is now divided into three deliberate steps.

## Phase 2A — Architecture & Data Model

**Completed**

Freeze and document the fundamental catalogue model:

- Photo vs. File vs. FileVersion
- logical vs. physical identity
- SHA-256 and content identity
- multiple files per Photo
- derived Photos and provenance
- Findings
- scan roots and scan runs
- missing/unavailable files and roots
- deterministic scanning
- audit events
- configuration and reproducibility
- metadata provenance
- recovery and rebuild principles

A normal rescan preserves catalogue identities.

A deliberate **fresh total rebuild may create new opaque IDs**, while the catalogue retains enough deterministic evidence to support future recovery/reconciliation if an old catalogue or manifest is available.

---

## Phase 2B — Data Inspector

**Next**

Build a read-only developer/admin interface for inspecting the SQLite catalogue.

The inspector should make it possible to answer:

```text
Why does this Photo exist?
Which Files belong to it?
Where have those Files been?
Which FileVersions exist?
Why is something missing?
Which ScanRun discovered it?
Which configuration was used?
Why is something a Finding?
How was a Finding classified?
What is the provenance of this information?
```

Initial areas:

```text
Dashboard
Photos
Files
FileVersions
Findings
Scan Roots
Scan Runs
Events
Configuration
Relationships
```

Phase 2B is important because it gives us a way to **observe and validate the catalogue before making the scanner significantly more complex**.

---

## Phase 2C — Deterministic Catalogue / Scanner

**After the Data Inspector**

Implement the complete deterministic filesystem → catalogue pipeline:

```text
Filesystem
    ↓
Discovery
    ↓
Candidate classification
    ↓
File observation
    ↓
Content + metadata extraction
    ↓
Identity matching
    ↓
Catalogue update
    ↓
Audit events
    ↓
SQLite catalogue
    ↓
Data Inspector
```

This phase includes:

- scan orchestration
- ScanRoot handling
- deterministic discovery
- supported-file detection
- exclusions
- File identity
- FileVersion creation
- SHA-256 hashing
- basic metadata extraction
- Photo association
- Findings
- missing detection
- scan history
- configuration snapshots
- audit events
- crash recovery
- cancellation
- incremental rescanning
- deterministic behaviour

Testing proceeds from:

```text
synthetic test datasets
        ↓
small real directory
        ↓
larger collection subset
        ↓
full photo collection
```

The goal is a genuinely useful catalogue **without AI or sophisticated image analysis**.

---

# Phase 3 — Metadata

Once the deterministic catalogue is reliable, expand metadata handling.

Add:

```text
MetadataObservation
Canonical metadata
Metadata provenance
```

Extract and reconcile:

```text
EXIF
XMP
filesystem metadata
manual/catalog metadata
```

Metadata should retain its provenance and competing observations rather than silently destroying information.

At this point Bilder should have a reliable, searchable description of the collection without needing AI.

---

# Phase 4 — Preservation

Once the catalogue knows what exists and what is missing, implement storage-management workflows:

```text
NAS preservation
quarantine
previously-deleted detection
restore workflow
```

This is where the principle

> **Maximum number of pictures on the NAS first**

becomes operational.

The catalogue should be able to distinguish between:

```text
known and safely preserved
known but missing
new
deleted
quarantined
restorable
```

Preservation should build on the deterministic catalogue rather than being responsible for discovering what the collection contains.

---

# Phase 5 — Search and Collection Management

Once the catalogue contains substantial real-world data, build useful search and collection capabilities:

```text
date
location
person
tag
format
source
collection
state
```

This is the point where Bilder becomes a practical photo-management application rather than primarily a catalogue/scanner.

Search should operate on the structured catalogue rather than repeatedly scanning the filesystem.

---

# Phase 6 — Advanced Analysis

Only after the deterministic foundation, metadata, preservation and search systems are reliable:

```text
pHash
pixel similarity
visual similarity
faces
clustering
AI proposals
metadata correction proposals
discovery
```

These systems may suggest relationships or metadata, but they should build on the deterministic catalogue rather than replacing it.

The general principle remains:

```text
Deterministic facts
       ↓
Structured catalogue
       ↓
Metadata
       ↓
Preservation
       ↓
Search
       ↓
Probabilistic / AI analysis
```

AI can propose; the catalogue remains authoritative.