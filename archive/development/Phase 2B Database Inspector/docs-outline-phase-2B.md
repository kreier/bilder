# Bilder — Phase 2B Outline: Data Inspector

**Status:** Planned  
**Phase:** 2B  
**Prerequisite:** Phase 2A Architecture & Data Model frozen

## 1. Purpose

Phase 2B builds a developer/admin **Data Inspector** for the Bilder catalog.

Its purpose is not to provide the final user-facing photo application.

Its purpose is to make the catalog state visible and understandable so that:

- the Phase 2A model can be validated against the actual SQLite implementation,
- test data can be inspected easily,
- relationships and historical state can be verified,
- scanner behavior can later be diagnosed,
- and database problems can be investigated without directly querying SQLite.

The Data Inspector should become the project's **microscope into the catalog**.

---

## 2. Guiding principles

### 2.1 Read-only initially

The first version should not modify catalog data.

It should inspect and explain the database rather than become another source of business logic.

### 2.2 Database-oriented, not filesystem-oriented

The Inspector primarily answers:

> "What does the catalog currently believe?"

It should not initially attempt to rescan directories or perform catalog operations.

### 2.3 Expose relationships

The Inspector should make relationships easy to follow.

For example:

```text
Photo
  ├── Files
  │    ├── FileVersions
  │    └── paths/history
  └── Derivations
```

Likewise:

```text
ScanRun
  ├── Roots
  └── Events
```

### 2.4 No duplicated domain logic

The Inspector should use the project's database/domain layer.

It should not implement a second interpretation of:

- Photo identity,
- File identity,
- missing state,
- scan status,
- provenance,
- configuration,
- or other catalog rules.

---

## 3. Initial scope

The first Inspector should provide views for:

### Dashboard

A compact overview of:

- database status,
- number of Photos,
- Files,
- FileVersions,
- Findings,
- ScanRoots,
- ScanRuns,
- recent events,
- missing objects,
- and other useful high-level counts.

### Photos

List and inspect individual Photos.

Show:

- Photo ID,
- lifecycle/status,
- associated Files,
- FileVersions,
- provenance,
- derivations,
- relevant metadata,
- and history.

### Files

List and inspect physical/cataloged Files.

Show:

- File ID,
- associated Photo,
- current path,
- state,
- current version,
- hash,
- size,
- timestamps,
- and version history.

### FileVersions

Inspect the historical states of a File.

Show:

- version ID,
- hash,
- physical properties,
- associated Photo,
- metadata observations where available,
- creation/observation information,
- and relevant scan events.

### Findings

Inspect unassociated filesystem findings.

Show:

- Finding ID,
- path,
- classification/state,
- available evidence,
- history,
- and eventual classification relationship where applicable.

### Scan Roots

Inspect configured roots.

Show:

- root identity,
- path,
- label,
- enabled state,
- configuration version,
- last scan,
- and scan history.

### Scan Runs

Inspect complete scan executions.

Show:

- ScanRun ID,
- status,
- timestamps,
- selected roots,
- configuration snapshot,
- root results,
- and summary events.

### Events

Provide a chronological/event-oriented view of catalog history.

Support filtering by:

- ScanRun,
- root,
- Photo,
- File,
- Finding,
- event type,
- actor,
- and time.

### Configuration

Allow inspection of the configuration snapshot associated with a scan.

The initial version does not need to provide configuration editing.

---

## 4. Relationship navigation

A major purpose of the Inspector is to allow navigation between related objects.

Examples:

```text
Photo
  → File
      → FileVersion
          → ScanEvent
```

and:

```text
Photo
  → Derived Photo
  → Source Photo
```

and:

```text
ScanRun
  → ScanRoot
      → Events
      → discovered Files
      → Findings
```

Every important object should provide links to related objects.

---

## 5. Test-data support

The Inspector should work with deliberately constructed test databases.

Before Phase 2C, create small datasets representing important Phase 2A cases, such as:

- one Photo / one File,
- one Photo / multiple Files,
- exact duplicate Files,
- moved File,
- renamed File,
- changed FileVersion,
- Photo with no Files,
- derived Photo,
- multiple-parent derivation,
- Finding,
- classified Finding,
- missing root,
- incomplete scan,
- cancelled scan,
- configuration change.

The purpose is to verify that the database model is understandable when observed through the Inspector.

---

## 6. Validation goals

Before declaring Phase 2B complete, it should be possible to answer questions such as:

- Why does this Photo exist?
- Which physical Files represent it?
- Where have those Files been?
- What versions did a File have?
- Why is this Photo currently missing?
- When was it last observed?
- Which scan discovered it?
- What configuration was active?
- Why was a Finding created?
- How was a Finding later classified?
- What is the provenance of a derived Photo?
- What happened during a particular scan?

If these questions cannot be answered from the database and Inspector, revisit the data model before proceeding.

---

## 7. Implementation sequence

### Step 1 — Inspector foundation

- Establish the Inspector application structure.
- Connect it to SQLite through the project's data layer.
- Add basic layout/navigation.
- Establish development/debug configuration.

### Step 2 — Database overview

- Dashboard.
- Basic counts.
- Database health/status.

### Step 3 — Core entities

Implement inspection of:

1. Photos
2. Files
3. FileVersions
4. Findings

### Step 4 — Scan history

Add:

1. ScanRoots
2. ScanRuns
3. root results
4. ScanEvents

### Step 5 — Relationship navigation

Connect the entity views so that related objects can be followed.

### Step 6 — Configuration and provenance

Expose:

- configuration snapshots,
- configuration hashes,
- provenance,
- derivation relationships,
- and relevant history.

### Step 7 — Test datasets

Create representative catalog states and inspect them through the UI.

### Step 8 — Model validation

Use the Inspector to identify:

- missing relationships,
- ambiguous states,
- confusing terminology,
- insufficient historical information,
- or schema problems.

Fix architectural/data-model problems before starting 2C.

---

## 8. Explicitly out of scope

Phase 2B should not become the final photo application.

Do not initially build:

- photo editing,
- photo organization,
- AI suggestions,
- automatic identity matching,
- sophisticated image search,
- bulk catalog modification,
- metadata editing,
- source-file modification,
- user accounts/permissions,
- final public-facing UI.

Write operations can be added later if they become useful for administration, but the initial Inspector should remain read-only.

---

## 9. Completion criterion

Phase 2B is complete when the SQLite catalog can be **visually inspected and understood well enough to validate the Phase 2A model before the deterministic scanner is implemented.**

The key question is:

> **Can we look at the database and understand what the catalog knows, what it does not know, and why?**

---

## 10. Transition to Phase 2C

Once the Inspector validates the model:

```text
Phase 2A
Architecture & Data Model
        ↓
Phase 2B
Data Inspector
        ↓
validated catalog model
        ↓
Phase 2C
Deterministic Catalog/Scanner
```

Phase 2C can then concentrate on producing correct catalog state rather than simultaneously discovering whether the underlying model is adequate.