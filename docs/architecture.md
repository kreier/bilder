# Bilder — Architecture

## Status

This document describes the planned architecture of Bilder.

It is a design document, not a description of an already implemented system. Components should be introduced incrementally as the project develops.

The current repository is still in the architecture and design phase.

## High-Level Architecture

The intended system consists of a central Bilder server running on a Raspberry Pi, connected to the canonical photo archive on the NAS.

Users interact primarily through a web browser.

Apple Photos and iCloud Photos are accessed through a separate macOS bridge because Apple's Photos framework is available to native Apple applications rather than directly to the Raspberry Pi.

```text
                         ┌──────────────────────┐
                         │       Browser        │
                         │    Web Interface     │
                         └──────────┬───────────┘
                                    │
                              HTTP / API
                                    │
                         ┌──────────▼───────────┐
                         │    Bilder Server     │
                         │     Raspberry Pi     │
                         │                       │
                         │  API / Application   │
                         │  Database            │
                         │  Workers             │
                         └───────┬───────┬───────┘
                                 │       │
                     ┌───────────┘       └──────────────┐
                     │                                  │
              ┌──────▼──────┐                   ┌──────▼──────┐
              │     NAS      │                   │   External  │
              │              │                   │   Sources   │
              │   Canonical  │                   │             │
              │   Originals  │                   │ Google Drive│
              │   Thumbnails │                   │ Backups     │
              │   etc.       │                   │ Camera/SD   │
              └─────────────┘                   └─────────────┘


                    ┌─────────────────────────┐
                    │     macOS Bridge        │
                    │    Native Swift App     │
                    └────────────┬────────────┘
                                 │
                              PhotoKit
                                 │
                    ┌────────────▼────────────┐
                    │ Apple Photos / iCloud   │
                    └─────────────────────────┘
```

## Components

### 1. Web Browser

The browser is the primary user interface.

It should eventually provide functionality such as:

- photo browsing
- search
- filtering
- metadata inspection
- duplicate review
- source comparison
- operation previews
- approval of destructive operations
- system status
- statistics

The browser should communicate with the server through an authenticated HTTP API.

The browser should not access the NAS directly.

## 2. Bilder Server

The Bilder server is the central application.

The planned implementation is:

- Python
- FastAPI
- SQLite
- background workers

The server is responsible for:

- exposing the API
- managing the database
- maintaining photo and file identities
- cataloging sources
- coordinating scanning
- initiating analysis
- generating operation proposals
- maintaining operation history
- serving metadata and thumbnails
- communicating with external bridges

The server is the central coordination point, but it should not unnecessarily perform CPU-intensive processing inside HTTP request handlers.

## 3. Database

SQLite is the planned initial database.

The database contains the catalog and system state, rather than the actual photographs.

It will eventually represent concepts such as:

- logical photographs
- file versions
- sources
- source copies
- metadata
- hashes
- visual similarity information
- thumbnails
- operations
- operation results
- provenance
- audit history

The actual database is private and must never be committed to the public repository.

The repository should contain database schema definitions and migrations as the implementation develops.

## 4. Background Worker

Photo processing can be computationally expensive and should be separated from interactive API requests.

The worker layer is intended to perform tasks such as:

- filesystem scanning
- ExifTool metadata extraction
- SHA-256 calculation
- perceptual hashing
- thumbnail generation
- image analysis
- source synchronization
- verification
- filesystem operations

Long-running tasks should have identifiable jobs and recorded results.

The worker should operate through explicit, controlled tasks rather than silently modifying the collection.

## 5. NAS

The NAS is the canonical storage layer.

The Bilder server accesses the NAS through a controlled filesystem mount.

The NAS should remain understandable and usable independently of the application.

Potential safety-oriented directories may eventually include locations such as:

```text
_inbox/
_quarantine/
_deleted/
```

These are conceptual examples at this stage; the exact filesystem structure should be defined separately before implementation.

Bilder should avoid making assumptions that make the photo archive dependent on a particular database state.

## 6. macOS Bilder Bridge

The macOS bridge is a native application written in Swift.

Its purpose is to provide a controlled connection between Bilder and Apple's Photos ecosystem.

The bridge communicates with:

```text
Bilder Server
      │
      ▼
macOS Bilder Bridge
      │
      ▼
   PhotoKit
      │
      ▼
Apple Photos / iCloud Photos
```

The bridge may eventually:

- enumerate Photos assets
- retrieve metadata
- retrieve thumbnails
- retrieve original resources where permitted
- calculate hashes
- send catalog information to the Bilder server
- receive approved operations
- perform changes through PhotoKit
- report operation results

The bridge should not expose the user's Photos library directly to the web browser.

## 7. Apple Photos / iCloud

Apple Photos is treated as an external source.

Apple/iCloud identifiers are source-specific identifiers and must remain separate from Bilder's internal identifiers.

For example:

```text
Bilder photo_id
       │
       ├── NAS file version
       ├── Google Drive copy
       └── Apple Photos asset
                 │
                 └── Apple/iCloud identifier
```

The Bilder `photo_id` is the stable identity used by Bilder.

An Apple identifier identifies the corresponding asset in Apple's ecosystem.

## 8. Other External Sources

The architecture should support additional sources without making them part of the core storage layer.

Possible sources include:

- Google Drive
- phone backups
- camera cards
- exported photo folders
- removable storage
- other filesystem collections

Each source should be identifiable and cataloged.

The system should be able to compare source contents with the canonical NAS archive without automatically modifying the source.

## Data Flow

### Initial Discovery

A typical discovery process should look like:

```text
Source
  │
  ▼
Scanner
  │
  ├── filename/path
  ├── file size
  ├── timestamps
  ├── metadata
  ├── SHA-256
  └── visual hash
  │
  ▼
Bilder Database
```

The scanner records what it finds.

Discovery should initially be read-only.

### Matching

After discovery, the server can compare files against existing catalog entries.

Matching may use:

1. exact SHA-256 match
2. existing source identifiers
3. metadata
4. visual similarity
5. additional heuristics

A match should produce a relationship or recommendation rather than immediately changing files.

### Importing a File

An eventual import workflow may look like:

```text
External Source
      │
      ▼
Discovery
      │
      ▼
Comparison
      │
      ▼
User Approval
      │
      ▼
Copy / Import
      │
      ▼
Verification
      │
      ▼
Canonical NAS
      │
      ▼
Database updated
```

The imported file should be verified after copying.

### Duplicate Handling

Duplicate handling should follow:

```text
Detect
  ↓
Compare
  ↓
Present candidates
  ↓
User decision
  ↓
Quarantine
  ↓
Verify
  ↓
Optional permanent deletion
```

There should be no implicit:

```text
duplicate detected → delete
```

relationship.

## Identity and File Versions

The architecture separates four concepts:

| Concept | Purpose |
|---|---|
| `photo_id` | Stable logical identity of a photograph |
| `file_version_id` | Identity of a particular stored file version |
| SHA-256 | Exact byte-level identity of a file |
| pHash | Approximate visual similarity |

A source can additionally provide its own identifier.

For example:

```text
photo_id:        logical photograph
     │
     ├── file_version A
     │      └── SHA-256 A
     │
     ├── file_version B
     │      └── SHA-256 B
     │
     ├── NAS canonical copy
     │
     ├── Google Drive copy
     │
     └── Apple Photos asset
            └── Apple source identifier
```

Changing metadata can create a different file hash while preserving the same logical `photo_id`.

## Metadata and Identity

Original files should initially be preserved without modification.

If Bilder later embeds its own `photo_id` into XMP or another supported metadata location, the modified file becomes a new file version.

For example:

```text
Original file
    │
    ├── SHA-256: A
    │
    ▼
Metadata added
    │
    ▼
Canonical file version
    │
    └── SHA-256: B
```

The logical photograph remains the same:

```text
photo_id = X
```

This provides a useful distinction between logical identity and physical file content.

## Security Boundaries

The system has several trust boundaries.

### Browser → Bilder Server

The browser communicates with the authenticated server API.

The server must validate requests and enforce authorization before performing operations.

### Bilder Server → NAS

The server has access to the photo archive and therefore represents a high-trust component.

Filesystem permissions should follow least privilege where practical.

Operations affecting files should be explicit and auditable.

### Bilder Server → macOS Bridge

Communication with the macOS bridge must be authenticated.

The bridge should accept commands only from the authorized Bilder server.

Operations should have explicit identities and results so that failures can be diagnosed.

### macOS Bridge → Photos

The bridge operates through Apple's supported PhotoKit framework and the permissions granted to the application.

The bridge should not depend on private iCloud protocols.

## Failure and Recovery

The architecture should assume that components can fail.

Examples include:

- NAS temporarily unavailable
- network connection interrupted
- worker process crashes
- macOS bridge offline
- Photos library unavailable
- database unavailable
- operation interrupted halfway through
- file copy succeeds but database update fails

Operations should therefore be designed so that they can be resumed or reconciled.

For file-changing operations, the system should verify the resulting state instead of assuming success.

## Database Loss

The database is important but should not be the only representation of the collection.

The system should aim for recovery through:

- original filesystem structure
- file metadata
- embedded identifiers where appropriate
- SHA-256 hashes
- source identifiers
- database backups

The exact recovery process should be documented separately once the data model is defined.

## Privacy Boundary

The public source repository and the private photo system are deliberately separate.

```text
PUBLIC
GitHub repository
├── source code
├── architecture
├── schemas
├── tests
└── sanitized examples

PRIVATE
Personal environment
├── photos
├── NAS
├── database
├── cloud identifiers
├── filesystem paths
└── credentials
```

The application may generate aggregate statistics for public display, but such data should pass through an explicit sanitization/allowlist process.

## Implementation Strategy

The architecture should be implemented in stages.

A sensible progression is:

1. Documentation and architecture
2. Data model
3. Database schema
4. Read-only filesystem scanner
5. Metadata extraction
6. SHA-256 file identification
7. Thumbnail generation
8. Basic web catalog
9. Duplicate detection
10. Safe filesystem operations and quarantine
11. External source cataloging
12. macOS bridge
13. Apple Photos/iCloud integration
14. Additional external sources such as Google Drive

Each stage should produce a useful and testable result before the next major subsystem is introduced.

## Current vs. Planned

At the current stage, the following are **design targets**, not necessarily implemented components:

- Raspberry Pi server
- FastAPI API
- SQLite database
- background worker
- NAS integration
- browser frontend
- macOS Swift bridge
- PhotoKit integration
- duplicate detection
- external source synchronization

The repository should not imply that these components already exist merely because they are described in this document.

The architecture is intentionally ahead of implementation so that major design decisions can be reviewed before personal data is introduced.