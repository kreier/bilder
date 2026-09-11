# Bilder — Phase 2B: Data Inspector Specification

**Status:** Active  
**Phase:** 2B — Data Inspector  
**Prerequisites:** Phase 2A Architecture & Data Model frozen  

---

## 1. Purpose

Phase 2B creates a developer and administrative **Data Inspector** for the Bilder catalog.

The Data Inspector is **not** the final end-user photo application. Rather, it serves as the project's **microscope into the catalog**. Its primary objectives are:

1. **Model Validation:** Validate the frozen Phase 2A conceptual model against the concrete SQLite implementation.
2. **State Transparency:** Inspect test datasets and examine how photos, files, versions, and events are represented.
3. **Relationship Verification:** Trace connections between logical Photos, physical Files, historical FileVersions, and provenance derivations.
4. **Diagnostic Readiness:** Provide the diagnostic tooling needed before the deterministic scanner pipeline is implemented in Phase 2C.
5. **Direct Investigation:** Allow inspecting and debugging catalog data without having to write ad-hoc SQL queries.

---

## 2. Guiding Principles

### 2.1 Read-Only Initially
The initial Data Inspector must not modify catalog data. It explains and displays what the database contains; it does not introduce new catalog mutation or business logic.

### 2.2 Database-Oriented, Not Filesystem-Oriented
The Inspector answers:
> *"What does the catalog currently believe, and what is the recorded provenance?"*

It observes database state rather than triggering live filesystem rescans or performing automated disk operations.

### 2.3 Expose Relationships & History
Relationships must be first-class and clickable:
```text
Photo ───< File ───< FileVersion ───< ScanEvent
  │
  └───< PhotoDerivation (source / derived)

ScanRun ───< ScanRoot
   │
   └───< ScanEvent
   │
   └───< Finding
```

### 2.4 No Duplicated Domain Logic
The Inspector relies directly on the underlying database queries and domain models. It does not introduce separate or conflicting definitions of photo identity, file state, or scan outcomes.

---

## 3. Scope of Views

The Data Inspector provides views for the following areas:

### 3.1 Dashboard / Overview
High-level summary of catalog health:
- Counts: Photos (active vs. missing), Files (present vs. missing), FileVersions, Findings (unclassified vs. classified), ScanRoots, ScanRuns.
- Latest ScanRun details: root, status, start/finish times, summary counts, error states.
- Recent ScanEvents log.

### 3.2 Photos View
Browse and inspect logical Photos:
- **List:** Filter by state (`active`, `missing`), search by ID.
- **Detail:**
  - Photo ID and lifecycle state.
  - Associated physical Files.
  - Current effective metadata (capture date, camera, dimensions, etc.).
  - Derivations (source Photos, derived Photos, derivation type).
  - Chronological history of events related to this Photo.

### 3.3 Files View
Browse and inspect physical cataloged Files:
- **List:** Filter by state (`present`, `missing`, `excluded`), search by path/filename.
- **Detail:**
  - File ID and parent Photo ID.
  - Current tracked path and filename.
  - Lifecycle state.
  - Current FileVersion (SHA-256, file size, filesystem mtime).
  - Version history (all historical FileVersions observed at this path).

### 3.4 FileVersions View
Inspect observed byte states:
- **List / Search:** Search by SHA-256 hash or size.
- **Detail:**
  - Version ID, SHA-256, byte size.
  - First seen timestamp and ScanRun.
  - Associated File(s) and Photo(s).
  - Technical metadata observations (dimensions, EXIF payload).

### 3.5 Findings View
Inspect unclassified or candidate filesystem objects:
- **List:** Filter by status (`current`, `missing`, `classified`), extension, or path.
- **Detail:**
  - Finding ID, path, filename, size, detected format.
  - Classification state and classification history.
  - Associated File ID (if later classified).
  - Discovery ScanRun and recorded evidence.

### 3.6 Scan Roots View
Inspect configured scanning locations:
- **List:** Configured roots, active/enabled status, paths, labels.
- **Detail:**
  - Root ID, canonical path, configuration options (include/exclude patterns, extensions).
  - Scan history (all ScanRuns targeting this root).
  - Current status (e.g. available vs. unavailable/offline).

### 3.7 Scan Runs View
Inspect individual scanner executions:
- **List:** Filter by status (`running`, `completed`, `failed`, `cancelled`, `partial`).
- **Detail:**
  - ScanRun ID, scanner version, configuration snapshot and hash.
  - Target root(s) and per-root outcomes.
  - Start time, completion time, duration.
  - Aggregated event counts (new files, unchanged, modified, missing, errors).
  - Detailed list of errors or warnings encountered.

### 3.8 Events View
Chronological audit stream of catalog changes:
- Append-only event log with filtering by:
  - ScanRun ID
  - Root ID
  - Event type (`file_discovered`, `file_modified`, `file_missing`, `version_created`, `error`, etc.)
  - Timestamp range

### 3.9 Configuration View
Inspect effective system and scanner configuration:
- View current configuration values.
- Inspect historical configuration snapshots captured during past ScanRuns.

---

## 4. Relationship Navigation

The Inspector UI must make cross-entity navigation effortless:
- Clicking a `Photo ID` anywhere opens the Photo detail view.
- In the Photo detail view, clicking an associated `File` navigates to that File's detail.
- In the File detail view, clicking a `SHA-256` or `Version ID` navigates to that FileVersion.
- Clicking a `ScanRun ID` opens the ScanRun inspection view with all associated events.
- In a `Finding` that was classified, clicking the target `File ID` jumps directly to the cataloged File.

---

## 5. Validation Goals & Completion Criteria

Phase 2B is complete when the Inspector enables answering all of the following questions directly through the interface:

1. **Why does this Photo exist?** (Which File(s) or derivation created it?)
2. **Which physical Files represent it?** (Where are they located on disk?)
3. **Where have those Files been?** (What is their path history across scans?)
4. **What byte versions has a File had?** (What changed between FileVersions?)
5. **Why is a Photo marked missing?** (Are all its associated Files missing or deleted?)
6. **Which ScanRun discovered a particular object?** (What configuration was active at that time?)
7. **Why was an object flagged as a Finding?** (What made it unclassifiable at discovery time?)
8. **What happened during a specific scan run?** (Which roots were processed, how many files changed, what errors occurred?)

Once these questions can be answered with confidence against test datasets, the model is validated and development proceeds to **Phase 2C (Deterministic Catalog/Scanner)**.
