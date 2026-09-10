# Bilder — Architecture

## Status

This document describes the planned architecture of Bilder.

It is a design document, not a description of an already implemented system. Components should be introduced incrementally.

## Architectural Principles

Bilder is a **preservation-first catalogue and management system around a canonical NAS archive**.

- **The NAS is canonical storage.**
- **Discovery is non-destructive.** Scanning observes; it does not silently import, move, rename, or delete.
- **Preserve before reducing.** A newly discovered photographic file that is not represented on the NAS should first be preserved there.
- **Duplicates are an optimization problem, not an ingestion problem.** Detection should not automatically cause deletion.
- **Explicit deletion is required.** Permanent deletion must be deliberate and documented.
- **History matters.** Sources, observations, locations, versions, metadata, and operations remain historically understandable.
- **The database is authoritative for catalogue meaning; the filesystem records physical location.**
- **The archive should remain useful without Bilder.** The NAS filesystem should have meaningful human-readable organization.
- **Probabilistic analysis produces proposals.** AI and similarity analysis must not silently overwrite user decisions.

> **Bilder should first understand and preserve the archive, then help the user organize and reduce it.**

## High-Level Architecture

The intended system consists of a Bilder server running on a Raspberry Pi, connected to the canonical NAS archive. Users interact through a web browser. Apple Photos/iCloud is accessed through a separate native macOS bridge using PhotoKit.

```text
Browser
   │ HTTP / API
   ▼
Bilder Server (Raspberry Pi)
   ├── API / Application
   ├── SQLite database
   └── Background workers
       │
       ├──────────────► NAS — canonical archive
       │
       └──────────────► External sources
                              ├── old HDDs
                              ├── Google Drive
                              ├── camera / SD
                              └── other collections

Bilder Server ◄──► macOS Bridge (Swift) ◄── PhotoKit ◄── Apple Photos / iCloud
```

## Components

### Web Browser

The browser is the primary UI for browsing, search, filtering, metadata inspection, source comparison, scan results, duplicate review, proposals, and approval of destructive operations.

It communicates with the server API and does not access the NAS directly.

### Bilder Server

The planned implementation is:

- Python
- FastAPI
- SQLite
- background workers

The server coordinates:

- the catalogue
- sources
- scans
- metadata
- analysis
- proposals
- operations
- thumbnails
- external bridges

CPU-intensive work should not run inside normal HTTP request handlers.

### Database

SQLite is the planned initial database.

The database stores catalogue and system state, not the photographs themselves.

It will eventually represent concepts such as:

- Photos
- MediaFiles
- MediaFile relationships
- FileVersions
- Sources
- SourceCopies
- ScanSessions
- FileObservations
- metadata observations
- hashes and fingerprints
- faces
- people
- tags
- collections
- operations
- proposals
- decisions
- provenance
- audit history

The private database must never be committed to the public repository.

The repository should eventually contain database schema definitions and migrations.

### Background Workers

Workers perform long-running tasks such as:

- filesystem scanning
- metadata extraction
- SHA-256 calculation
- perceptual hashing
- thumbnail generation
- image analysis
- face analysis
- preservation copies
- verification
- controlled filesystem operations

Jobs and results should be identifiable and auditable.

Workers should operate through explicit, controlled tasks rather than silently modifying the collection.

## NAS

The NAS is the canonical preservation target.

The NAS should remain understandable and usable independently of Bilder.

A possible physical organization is:

```text
Photos/
├── 2013/
│   ├── 07-14_America_Trip/
│   └── 08-03_Johns_Wedding/
├── 2014/
│   └── ...
├── ...
├── 2026/
│   ├── 06-14_Dinner_with_Friends/
│   └── 09-10_Hardware_Benchmark/
├── benchmarks/
├── hardware_collection/
├── projects/
├── screenshots/
├── scans/
├── artwork/
├── documents/
└── reference/
```

This is a design direction, not a requirement to create every directory.

Year/event folders and thematic areas are **physical organization only**.

The filesystem is deliberately not organized around people, tags, or collections because those are many-to-many logical relationships.

A photograph should not need to be duplicated physically merely because it belongs to several logical collections.

Potential `_inbox/` and `_quarantine/` areas may be defined later. Their exact structure is intentionally deferred.

### Physical Organization Principle

The filesystem should have useful meaning even when Bilder is unavailable.

For example:

```text
2026/
└── 04-12_Japan_Trip/
    ├── 04-12_Tokyo/
    ├── 04-13_Tokyo/
    └── 04-14_Kyoto/
```

The date prefix provides deterministic chronological sorting while the human-readable name provides contextual information.

The physical organization must not become the authoritative metadata model.

## macOS Bridge

A native Swift application provides controlled access to Apple Photos through PhotoKit.

It may eventually:

- enumerate Photos assets
- obtain metadata
- obtain thumbnails
- obtain original resources where permitted
- calculate hashes
- send observations to Bilder
- receive approved operations
- perform changes through PhotoKit
- report operation results

The bridge should not expose the Photos library directly to the browser.

The bridge should use supported PhotoKit APIs rather than private iCloud protocols.

## External Sources

Sources may include:

- Apple Photos / iCloud Photos
- Google Drive
- old HDD backups
- camera cards
- phone backups
- exported photo folders
- removable storage
- other filesystem collections

A Source represents a persistent physical or logical place/system/device.

A Source remains in the database even when it is offline, unplugged, retired, or otherwise unavailable.

Source identity should preferably be based on persistent physical or system identity rather than a temporary mount path.

For example, an HDD's serial/device identity is more useful than `/media/backup`.

## Discovery and Scan Model

Discovery is observation, not import.

```text
Source
  ↓
Discover files
  ↓
Filesystem metadata / path / size / timestamps
  ↓
SHA-256 as needed
  ↓
Recognize FileVersion
  ↓
Extract metadata
  ↓
Fingerprint / analyse where appropriate
  ↓
Compare catalogue
  ↓
Classify
  ↓
Preserve / review / ignore
```

Discovery and identification are separate:

- **Discovery** finds a file at a physical location.
- **Identification** determines which FileVersion it represents.
- **Classification** determines what should happen next.

### Scan Sessions

Scans are persistent historical sessions.

A ScanSession records information such as:

- Source
- start time
- end time
- scanner version
- scan depth
- configuration
- completion state
- progress
- counts
- errors

Detailed FileObservations allow historical comparison and reconstruction of scan summaries.

A conceptual scan summary could look like:

```text
NAS scan — 2026-09-01

Files scanned: 98,421
New files: 327
Known files: 97,812
Changed files: 41
Missing files: 12
Unknown files: 3
Errors: 0
Duration: 18m 42s
```

The summary is derived from detailed observations rather than being the only stored information.

### Missing Files

Missing files are determined by comparing completed observations.

A file should only be considered missing when a completed scan establishes that it was expected but was not observed.

The following must not automatically produce a missing state:

- source temporarily offline
- permission error
- network interruption
- scanner crash
- incomplete scan
- inaccessible directory

This distinction is important because:

```text
Not observed
```

does not necessarily mean:

```text
File deleted
```

### Scan Depth

Conceptual scan depths include:

#### Quick

- path
- size
- filesystem timestamps
- known-state checks

#### Normal

- SHA-256 for new or changed files
- metadata extraction
- media identification

#### Full Verification

- rehash files to verify exact contents

#### Deep Analysis

Expensive processing such as:

- perceptual hashes
- pixel fingerprints
- face detection
- face clustering
- video analysis

Deep analysis should normally be implemented as separate jobs rather than making every normal scan expensive.

### Hashing Strategy

Bilder should not unnecessarily calculate SHA-256 for every unchanged file during every normal scan.

A typical strategy is:

```text
Initial scan
    ↓
SHA-256 all relevant files

Later normal scan
    ↓
path + size + mtime
    ↓
unchanged → reuse known hash
changed/new → calculate SHA-256

Occasional verification
    ↓
SHA-256 everything requested
```

The scanner and extractor versions should be recorded so that future processing changes can be distinguished from historical observations.

## Preservation Invariant

The canonical NAS is the preservation target.

> **Every discovered photographic file should exist at least once on the NAS unless its deletion has been explicitly decided and documented.**

When an external source contains something absent from the NAS, the first concern is preservation, not duplicate reduction.

```text
External source
      ↓
   Discover
      ↓
Equivalent preserved file on NAS?
   ┌──┴──┐
  yes    no
   │      │
   │      ▼
   │   Preserve on NAS
   └──┬───┘
      ▼
   Catalogue
      ▼
Later optimization
```

The preservation rule concerns the discovered **file**, not merely the existence of some visually similar photograph.

For example, if an external source contains an HEIC and the NAS contains a JPEG representation of the same capture, Bilder should not assume that the JPEG is sufficient preservation of the HEIC. The HEIC should be preserved unless the user has explicitly established a different policy.

### Previously Deleted Files

If an old source contains a file that was previously deliberately deleted, Bilder should recognize this history.

It should report something similar to:

```text
Previously deleted file found

Source: HDD Backup 2019
File: IMG_1234.JPG
Previous deletion: 2025-04-12

What should happen?

[ Restore ]
[ Keep deleted ]
[ Ignore ]
```

The file must not automatically be restored simply because it has been rediscovered.

## Import / Preservation Workflow

Import and preservation are separate from scanning.

```text
SCAN
  ↓
DISCOVER
  ↓
COMPARE
  ↓
CLASSIFY
  ↓
USER DECISION where required
  ↓
COPY / PRESERVE
  ↓
VERIFY
  ↓
CATALOGUE
```

The external source should not be modified merely because Bilder discovered a file.

When copying to the NAS:

1. source file is read
2. destination file is written
3. destination is verified
4. resulting FileVersion is identified
5. SourceCopy is recorded
6. operation result is recorded

The system should not consider a preservation operation complete merely because the copy command returned successfully.

## Identity and File Versions

Bilder distinguishes between:

- the real-world photographic capture
- a logical media representation
- an exact byte-level version
- a physical copy of that version

Conceptually:

```text
Photo / capture
   │
   ├── MediaFile: still
   │      ├── FileVersion A
   │      └── FileVersion B
   │
   └── MediaFile: motion companion
          └── FileVersion C
                  ├── SourceCopy: NAS
                  ├── SourceCopy: HDD
                  └── SourceCopy: cloud
```

### Photo

A `photo_id` identifies one real-world photographic capture.

One Photo may therefore contain multiple related media files.

Examples:

- iPhone Live Photo still + companion MP4
- RAW + derived JPEG
- original + edited representation
- alternate representations of the same capture

Five individual burst photographs are five Photos. No special burst entity is required at this stage.

### MediaFile

A MediaFile represents one logical media representation of a Photo.

For example:

```text
Photo
├── ARW
└── JPG
```

The ARW and JPG may be separate MediaFiles even when they represent the same capture.

### MediaFile Relationships

Relationships connect MediaFiles, not FileVersions or SourceCopies.

Useful conceptual relationship types are:

- `companion`
- `derived`
- `edited`
- `alternate`

Relationships are directional where derivation matters and symmetric where it does not.

For example:

```text
ARW ──derived──► JPG
```

while:

```text
HEIC ──companion── MP4
```

does not imply that one is derived from the other.

### FileVersion

A FileVersion represents an exact byte-level state of a MediaFile.

The SHA-256 hash identifies the exact bytes.

If metadata is changed, the bytes change and therefore a new FileVersion is created.

The logical Photo and MediaFile can nevertheless remain the same.

### SourceCopy

A SourceCopy represents one physical occurrence of a FileVersion at a Source.

For example:

```text
FileVersion
   ├── SourceCopy: NAS /Photos/2026/...
   ├── SourceCopy: HDD-2019 /DCIM/IMG_1234.JPG
   └── SourceCopy: Google Drive /Photos/...
```

If two physical locations contain exactly the same bytes, they reference the same FileVersion.

Moving a file changes its SourceCopy location/history, not its FileVersion.

### SourceCopy State

A SourceCopy may have states such as:

- `present`
- `missing`
- `deleted`
- `unknown`

A deleted physical copy should remain historically represented.

## Hashes and Fingerprints

Bilder may use several different kinds of hashes.

### SHA-256

Identifies exact file bytes.

```text
file_sha256
```

A metadata change changes the SHA-256.

### Content Hash

A format-aware hash intended to identify encoded media content while excluding metadata where this can be done reliably.

It should not be assumed to work identically for all formats.

### Pixel Hash

A hash calculated from decoded and normalized pixels.

This can identify visually identical content across some encoding differences and recompression.

RAW files require special care because rendering can vary.

### pHash

A perceptual hash used to find approximate visual similarity.

A pHash is evidence for a possible relationship, not proof that two files are the same photograph.

None of these replace `photo_id`.

## Metadata

Bilder uses two complementary layers.

### Canonical Photo Metadata

The Photo contains Bilder's current interpretation of capture information such as:

- capture time
- capture timezone
- GPS
- camera
- lens
- description

These values represent Bilder's current interpretation.

### File-Level Metadata

MediaFiles and FileVersions retain observations of information actually found in:

- EXIF
- XMP
- IPTC
- filesystem attributes
- external systems
- derived analysis

The database is authoritative for Bilder's canonical interpretation.

Embedded metadata remains evidence and a portability/synchronization mechanism.

Not every media format supports the same metadata mechanisms.

## Metadata Observations

Historical metadata observations should be retained.

A conceptual observation contains:

```text
field
value
source
observed_at
origin
confidence
```

Possible origins include:

- `embedded`
- `filesystem`
- `external_source`
- `derived`
- `user`

Keeping observations makes it possible to detect systematic errors.

For example:

```text
4132 photos
    │
    ├── EXIF time
    ├── filesystem time
    └── folder context
           │
           ▼
All appear to be shifted by +7 hours
           │
           ▼
Propose one correction
```

The system should not silently modify all 4132 photographs.

## Metadata Resolution

Bilder should use field-specific resolution rather than a universal precedence rule.

For example:

| Field | Strong evidence | Weaker/contextual evidence |
| --- | --- | --- |
| Capture time | EXIF DateTimeOriginal | filesystem time, folder context |
| Camera | EXIF Make/Model | external catalogue |
| GPS | embedded GPS | neighboring photos, folder context |
| Description | user assertion | embedded caption |
| Person identity | user decision | face recognition |

There should be no global rule such as:

```text
EXIF always wins
```

or:

```text
newest metadata always wins
```

Agreement between independent observations can increase confidence.

Outliers should be flagged rather than silently overwritten.

### Confidence vs. Authority

Confidence and authority are separate concepts.

For example:

```text
AI says: Anna, confidence 96%
User says: Maria
```

The AI result may have high confidence, but the user's decision has higher authority.

A user-entered correction should therefore not be silently undone by a later algorithm update.

### Canonical Metadata Status

Possible states include:

- `confirmed`
- `automatic`
- `proposed`
- `conflicted`
- `unknown`
- `rejected`

## Time Metadata

Capture time and filesystem times are different concepts.

Filesystem timestamps belong to the physical file/version context, for example:

- filesystem created
- filesystem modified
- imported at

Capture time belongs to the photographic capture.

Capture time should preserve timezone information when known.

Precision should also be preserved.

Possible precision values include:

- exact timestamp
- minute
- day
- month
- year
- unknown

If only a date is known, Bilder should not invent midnight as an exact capture time.

## Metadata Corrections

Large corrections should normally be proposed rather than automatically applied.

For example:

```text
Potential correction

Folder:
The_America_Trip

Photos affected:
4,132

Proposed change:
Capture time -7 hours

Strong matches:
4,118

Conflicts:
14

[ Review ]
[ Approve 4,118 ]
[ Review individually ]
```

The underlying data model remains photo-level and individually auditable even when the UI presents a group operation.

Folders are useful contextual grouping because they often correspond to days or events.

## Location

GPS coordinates and human-readable location are separate concepts.

A location may contain:

- latitude
- longitude
- precision
- source
- confidence
- canonical name

Possible location precision levels include:

- exact coordinate
- building / POI
- street
- neighborhood
- city
- region
- country
- unknown

Bilder should distinguish:

```text
Probably Paris
```

from:

```text
GPS: 48.8566, 2.3522
```

Inference from neighboring photographs, folders, timestamps, or AI can produce a proposal but should not automatically become an exact coordinate.

## Faces and People

Face processing is deliberately reversible.

```text
Photo
  └── FaceObservation
          └── FaceCluster
                  └── Person (optional)
```

### FaceObservation

Represents a detected face in a particular media representation.

It may contain:

- bounding box
- detection confidence
- landmarks where available
- representation analyzed
- processing model/version

### FaceCluster

Groups visually similar faces without assigning a name.

Clusters can exist anonymously.

### Person

A Person is a user-defined real-world identity.

A Person is not automatically created merely because an AI model produced a name.

### IdentityProposal

A recognition system can propose:

```text
Anna     96%
Maria    71%
Unknown   4%
```

This is a proposal rather than an identity assertion.

### IdentityDecision

User confirmation or rejection should be retained historically.

This allows:

- rejecting an identity
- overriding a cluster
- splitting a cluster
- merging clusters
- correcting individual face observations

The design specifically avoids irreversible assignment behavior.

`Unknown` is a valid state.

## Tags

Tags describe characteristics or subjects.

Tags should be structured entities rather than a comma-separated string.

Possible tag types include:

- Person
- Place
- Event
- Subject
- Object
- Activity
- Organization
- Custom

Specialized models such as Person and Location should remain separate rather than being reduced to generic tags.

Metadata imported from an external file is an observation.

A user-assigned tag is a user assertion.

An AI-generated tag is a proposal until accepted.

## Collections

Collections are distinct from Tags.

A useful distinction is:

```text
Tag
    = What characteristics apply?

Collection
    = Why do I want these Photos grouped?
```

A Photo may belong to many Collections.

Collections are logical and independent of physical storage.

A Collection may contain:

- name
- description
- date/date range
- location
- Photos

Collection membership should be explicit and persistent.

A saved search is different:

```text
Collection
    = explicit persistent membership

Saved Search
    = persistent query whose results may change
```

Existing filesystem folders may be imported as Collections, but Collection and folder should not become permanently identical.

## Search

Search primarily operates on Photos rather than individual physical files.

For example, an iPhone Live Photo should normally appear as one Photo rather than two search results.

Likewise, three identical copies on different sources should normally appear as one Photo.

Basic search dimensions include:

- date/time
- location
- person
- tags
- description
- media type
- file format
- collection
- source
- file state

Physical-layer queries should also be possible.

For example:

```text
Everything on HDD Backup 2019
but not currently present on NAS
```

Saved searches could include:

```text
Photos missing from NAS
Photos requiring time review
Previously deleted files found again
Photos with conflicting GPS
Files only present on old HDD
```

The internal search model should be structured so that:

- web UI
- API
- CLI
- future natural-language interface

can all use the same search engine.

A future LLM should translate natural language into structured search criteria rather than directly querying the database.

## Discovery

Discovery is intentionally separate from search.

Search answers:

```text
What do I already know about?
```

Discovery may eventually answer:

```text
What interesting relationships or groups exist that I have not explicitly asked for?
```

Examples might include:

- possible events
- possible trips
- clusters of similar photographs
- recurring locations
- previously unknown relationships

Discovery is deliberately deferred until the core catalogue and search model are stable.

## Physical Organization vs. Logical Organization

This distinction is fundamental.

### Physical Organization

The NAS filesystem answers:

```text
Where is this physical copy?
```

### Logical Organization

Bilder answers:

```text
What is this photograph?
Who is in it?
Where was it taken?
What event does it belong to?
Which collections contain it?
What other representations exist?
```

A Photo can therefore have:

```text
Physical location:
2026/08-23_Concert/IMG_1234.HEIC

Logical relationships:
Person = Anna
Location = Berlin
Tag = Concert
Collection = Summer 2026
```

The photo does not need to be physically duplicated into `Anna/`, `Berlin/`, or `Concert/`.

## Path History

Paths can change without changing the file's identity.

For example:

```text
2026/08-23_Concert/IMG_1234.HEIC
        ↓
2026/08-23_Concert/phone/IMG_1234.HEIC
```

If the bytes remain identical:

```text
same FileVersion
same MediaFile
same Photo
different SourceCopy location/history
```

Path history should therefore be retained rather than overwritten.

## Operations

Any operation that changes files or canonical state should have an identifiable Operation.

Examples:

- preserve external file to NAS
- move file
- rename file
- create quarantine copy
- quarantine original
- restore from quarantine
- permanent deletion
- metadata synchronization
- user-approved timestamp correction
- user-approved face identity

An Operation should record:

- intended action
- target
- requester
- creation time
- execution time
- result
- verification
- errors

## Proposals

A Proposal represents a recommended change that has not yet been accepted.

Examples:

- possible duplicate
- possible near duplicate
- timestamp correction
- GPS correction
- face identity
- metadata synchronization
- collection suggestion
- quarantine candidate

A proposal should never be treated as a completed action.

## Decisions

User decisions are durable historical information.

For example:

```text
Proposal:
IMG_1234 and IMG_5678 appear to be duplicates

Decision:
Keep IMG_1234
Quarantine IMG_5678
```

If the same detection algorithm runs again, Bilder should know that the user already made this decision.

Algorithm improvements must not silently erase user decisions.

## Audit and Provenance

Bilder should be able to explain its conclusions.

The system should eventually answer questions such as:

- Why does Bilder believe this capture time is correct?
- Where did this GPS value come from?
- Which file contained this metadata?
- Which scan discovered this file?
- When was it copied to the NAS?
- Which FileVersion is this?
- Why are these media files related?
- Why was this file proposed for quarantine?
- Why was it deleted?
- Which user decision established this person identity?

This is one reason historical observations should not simply be overwritten.

## Failure and Recovery

The architecture assumes that components can fail.

Examples include:

- NAS temporarily unavailable
- network connection interrupted
- worker process crashes
- macOS bridge offline
- Photos library unavailable
- database unavailable
- operation interrupted halfway through
- file copy succeeds but database update fails

Operations should therefore be resumable or reconcilable.

For file-changing operations, the system should verify the resulting state instead of assuming success.

### Interrupted Preservation

If a preservation copy is interrupted:

```text
Source
  ↓
partial destination
```

Bilder should not assume that the destination is valid.

It should verify the resulting file before considering the preservation complete.

### Database Failure

The filesystem should remain useful even if the database becomes unavailable.

Recovery should eventually make use of:

- original filesystem structure
- file metadata
- embedded identifiers where appropriate
- SHA-256 hashes
- source identifiers
- database backups

The exact database recovery procedure should be documented after the data model and schema are finalized.

## Security Boundaries

### Browser → Bilder Server

The browser communicates with the authenticated API.

The server must validate requests and enforce authorization before performing operations.

### Bilder Server → NAS

The server has high-trust access to the photo archive.

Filesystem permissions should follow least privilege where practical.

File-changing operations should be explicit and auditable.

### Bilder Server → macOS Bridge

Communication with the macOS bridge must be authenticated.

The bridge should accept commands only from the authorized Bilder server.

Operations should have explicit identities and results.

### macOS Bridge → Photos

The bridge operates through Apple's supported PhotoKit framework and the permissions granted to the application.

The bridge should not depend on private iCloud protocols.

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

The architecture should be implemented incrementally.

A sensible progression is:

1. Documentation and architecture
2. Data model
3. Database schema
4. Read-only filesystem scanner
5. Scan history and FileObservations
6. Metadata extraction and provenance
7. SHA-256 file identification
8. NAS preservation workflow
9. Thumbnails and basic web catalogue
10. Search
11. Duplicate/similarity analysis
12. Safe filesystem operations and quarantine
13. External source cataloguing
14. macOS bridge
15. Apple Photos/iCloud integration
16. Additional external sources
17. Advanced face analysis
18. Discovery

Each stage should produce a useful and testable result before the next major subsystem.

## Current vs. Planned

The following are design targets unless separately implemented and documented:

- Raspberry Pi server
- FastAPI API
- SQLite database
- background workers
- NAS integration
- browser frontend
- macOS Swift bridge
- PhotoKit integration
- duplicate detection
- external-source synchronization
- quarantine workflow
- face analysis
- discovery

The repository should not imply that these components already exist merely because they are described in this document.

The architecture is intentionally ahead of implementation so that major design decisions can be reviewed before personal data is introduced.
