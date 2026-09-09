# Bilder — Data Model

## Status

This document describes the conceptual data model for Bilder.

It is intentionally written before the SQLite schema is implemented. It defines the entities, their meaning, relationships, and important invariants.

The database tables, columns, indexes, foreign keys, migrations, and implementation-specific details should be derived from this model later.

---

# 1. Design Principles

The data model follows several principles.

## 1.1 Photo identity is not file identity

A photograph is a logical real-world capture.

A file is one representation of that capture.

The exact bytes of that file are a FileVersion.

A physical occurrence of that FileVersion is a SourceCopy.

Therefore:

```text
Photo
  └── MediaFile
        └── FileVersion
              └── SourceCopy
                    └── Source
```

These are deliberately separate concepts.

## 1.2 Physical copies are not separate photographs

If the same file exists on:

```text
NAS
HDD
Google Drive
```

there is one FileVersion and multiple SourceCopies.

It should not appear as three photographs.

## 1.3 Different representations may belong to one Photo

For example:

```text
Photo
├── HEIC
└── MP4 companion
```

or:

```text
Photo
├── ARW
└── JPG
```

The individual MediaFiles may have relationships to one another.

## 1.4 History is important

The database should preserve meaningful historical information.

It should be possible to determine:

- what was discovered
- where it was discovered
- when it was observed
- what metadata was found
- what changed
- what the user decided
- what operations were performed

The system should avoid unnecessarily replacing historical facts with only the latest state.

## 1.5 The NAS is the preservation target

The catalogue should support the invariant:

> Every discovered photographic file should exist at least once on the NAS unless its deletion has been explicitly decided and documented.

This is a preservation rule, not a duplicate-reduction rule.

## 1.6 User decisions have authority

Machine-generated conclusions are proposals.

User decisions are authoritative unless explicitly changed by the user.

# 2. Core Identity Model

The central hierarchy is:

```text
Photo
  │
  ├── MediaFile
  │       │
  │       └── FileVersion
  │               │
  │               └── SourceCopy
  │                       │
  │                       └── Source
  │
  └── MediaFile relationships
```

The entities answer different questions:

| Entity      | Question                                               |
| ----------- | ------------------------------------------------------ |
| Photo       | What real-world capture is this?                       |
| MediaFile   | What media representation belongs to that capture?     |
| FileVersion | What exact bytes constitute this representation?       |
| SourceCopy  | Where does that exact version physically exist?        |
| Source      | What storage system/device/service contains that copy? |

# 3. Photo

## Purpose

`Photo` represents one real-world photographic capture.

It is the stable logical identity of the photograph.

A Photo is not a filename, path, hash, or physical copy.

Conceptually:

```text
photo_id
```

should remain stable even if:

- a file is renamed
- a file is moved
- metadata is modified
- another copy is discovered
- another representation is imported

## Examples

### Live Photo

```text
Photo X
├── HEIC still
└── MP4 motion component
```

One Photo.

### RAW + JPEG

```text
Photo X
├── ARW
└── JPG
```

One Photo.

### Burst

Five independent captures:

```text
Photo A
Photo B
Photo C
Photo D
Photo E
```

No special burst entity is required at this stage.

## Canonical Photo Metadata

Photo may eventually contain canonical values such as:

- capture time
- capture timezone
- capture-time precision
- GPS/location
- camera
- lens
- description

These values represent Bilder's current interpretation.

The evidence supporting them is stored separately as observations.

# 4. MediaFile

## Purpose

A MediaFile represents one logical media representation belonging to a Photo.

It is independent of physical storage.

Examples:

```text
Photo
├── MediaFile: ARW
└── MediaFile: JPG
```

or:

```text
Photo
├── MediaFile: HEIC
└── MediaFile: MP4
```

A MediaFile can have multiple FileVersions over time.

## Why MediaFile Exists

Without MediaFile, it would be difficult to distinguish:

```text
same photo, different representation
```

from:

```text
same file, multiple physical copies
```

These are fundamentally different relationships.

# 5. MediaFileRelationship

## Purpose

Relationships between MediaFiles describe how representations relate to one another.

Relationships connect MediaFiles, not FileVersions or SourceCopies.

## Relationship Types

### companion

Two MediaFiles are parts of the same capture.

Example:

```text
HEIC ──companion── MP4
```

This relationship is symmetric.

### derived

One MediaFile was generated from another.

Example:

```text
ARW ──derived──► JPG
```

This relationship is directional.

### edited

One representation is an intentional edited version of another.

Example:

```text
Original JPG ──edited──► Edited JPG
```

This relationship is directional.

### alternate

Two representations belong to the same capture but their derivation relationship is unknown or irrelevant.

Example:

```text
HEIC ──alternate── JPG
```

This relationship is normally symmetric.

# 6. FileVersion

## Purpose

A FileVersion represents the exact byte-level state of a MediaFile.

Its primary exact identity is:

```text
SHA-256
```

For example:

```text
MediaFile X

FileVersion A
SHA-256 = abc...

FileVersion B
SHA-256 = def...
```

Both versions may belong to the same MediaFile.

## When a New FileVersion Is Created

A new FileVersion is required when file bytes change.

Examples:

- metadata is modified
- XMP is embedded
- image is edited
- file is otherwise rewritten

The Photo and MediaFile do not necessarily change.

## Important Invariant

If two SourceCopies have the same SHA-256:

```text
same FileVersion
```

They are not two FileVersions merely because they are on different sources.

# 7. Source

## Purpose


A Source represents a persistent place, system, device, or service where files can exist.

Examples:

```text
NAS
HDD Backup 2019
HDD Backup 2022
Google Drive
Apple Photos
Camera SD Card
Phone Backup
```
A Source is not simply a mount path.

## Source Identity

Source identity should preferably use persistent identity where available.

For a physical HDD, useful information might include:

- device serial number
- filesystem UUID
- manufacturer
- model
- capacity

A mount path such as:

```text
/media/backup
```

is not sufficient as the primary Source identity because it can change.

## Source Lifecycle

A Source may remain in the database after it becomes:

- offline
- unplugged
- retired
- unavailable
- replaced

Historical sources should not disappear merely because they are no longer connected.

# 8. SourceCopy

## Purpose

A SourceCopy represents one physical occurrence of a FileVersion at a Source.

Example:

```text
FileVersion X

SourceCopy A
Source = NAS
Path = /Photos/2026/08-23_Concert/IMG_1234.HEIC

SourceCopy B
Source = HDD-2019
Path = /DCIM/IMG_1234.HEIC
```

Both represent the same exact bytes.

## SourceCopy State

Possible states include:

- `present`
- `missing`
- `deleted`
- `unknown`

The exact implementation may evolve.

## Path Changes

Moving a file should not create a new FileVersion if the bytes remain unchanged.

For example:

```text
old path
    ↓
new path
```

results in a location change/history for the SourceCopy.

## Historical Copies

If a physical copy is deleted, its historical SourceCopy should remain represented.

This is important for auditability and recovery.

# 9. FileObservation

## Purpose

A FileObservation records what a scanner found at a particular Source and location during a ScanSession.

It is an observation, not necessarily a permanent identity assignment.

A conceptual observation may include:

- ScanSession
- Source
- path
- filename
- file size
- filesystem timestamps
- detected media type
- filesystem identifier
- SHA-256 when available
- scanner information
- observation time
- classification result

##Why Observations Exist

They allow Bilder to distinguish:

```text
file has disappeared
```

from:

```text
source has not been scanned recently
```
and:

```text
scanner encountered an error
```
They also preserve the history of discovery.

# 10. ScanSession

## Purpose

A ScanSession represents one execution of a scan against a Source.

It records historical scanning activity.

A ScanSession may contain:

- Source
- started_at
- completed_at
- scanner version
- scan depth
- configuration
- status
- progress
- number of files observed
- number of errors
- summary statistics

## Status

Possible conceptual states:

- `running`
- `completed`
- `failed`
- `cancelled`
- `partial`

An incomplete scan must not be interpreted as proof that missing files were deleted.

## Scan Depth

Possible values:

- `quick`
- `normal`
- `full`
- `deep`

Deep analysis may also be represented as separate jobs rather than a ScanSession.

# 11. Preservation State

Bilder needs to determine whether a discovered file is safely represented on the NAS.

A conceptual preservation state may distinguish:

- preserved
- needs preservation
- preservation in progress
- preservation verified
- previously deleted
- explicitly excluded
- unresolved

The exact state machine should be designed when the operational schema is implemented.

## Preservation Invariant

For every discovered photographic file:

```text
NAS SourceCopy exists
```

unless:

```text
explicit documented deletion decision exists
```

This rule is about preserving discovered files before optimization.

# 12. Deletion and Quarantine

## Quarantine

Quarantine is an intermediate physical state.

It allows the user to reduce the archive without immediately destroying data.

Conceptually:

present
  ↓
user approves reduction
  ↓
quarantine
  ↓
waiting period
  ↓
permanent deletion

A quarantined file remains catalogued.

Explicit Deletion

Permanent deletion should create a historical record containing information such as:

FileVersion
SourceCopy
deletion time
reason
decision
authorization
verification

This allows future discovery of the same file to be recognized as:

previously deliberately deleted

rather than automatically treated as a new import.

# 13. Hashes and Fingerprints

Bilder may maintain several forms of identity information.

SHA-256

Exact byte identity.

file_sha256

Changes whenever any byte changes.

Content Hash

A format-aware identity intended to represent encoded media content while ignoring metadata where practical.

The implementation must be format-specific.

Pixel Hash

A hash of decoded and normalized image pixels.

Useful for detecting visually identical images despite some encoding differences.

RAW formats require special handling because rendering can vary.

pHash

Perceptual similarity.

Useful for finding possible near-duplicates.

A pHash similarity does not prove:

same photograph

It only identifies a candidate relationship.

# 14. MetadataObservation
Purpose

A MetadataObservation records a value found or generated by a particular source at a particular time.

Conceptually:

field
value
source
observed_at
origin
confidence
Origins

Possible origins include:

embedded
filesystem
external_source
derived
user

Examples:

EXIF DateTimeOriginal
filesystem modified time
Apple Photos capture date
user-entered description
AI-inferred location
Historical Retention

Metadata observations should generally be retained.

This allows Bilder to identify systematic problems.

For example:

4132 files
EXIF time
+7 hours from expected time

may reveal a timezone error.

If only the corrected value were stored, the original evidence would be lost.

# 15. Canonical Metadata

The Photo contains Bilder's current canonical interpretation.

Examples:

capture_time
capture_timezone
capture_time_precision
location
camera
lens
description

Canonical metadata is not necessarily identical to any one embedded metadata value.

It is the result of the metadata resolution process.

Canonical Status

Possible statuses:

confirmed
automatic
proposed
conflicted
unknown
rejected

# 16. Metadata Resolution

Resolution is field-specific.

There is deliberately no global rule such as:

EXIF always wins

or:

newest observation wins

Different fields have different evidence quality.

Example:

Field	Strong evidence	Contextual evidence
Capture time	EXIF DateTimeOriginal	filesystem time, folder
Camera	EXIF Make/Model	external source
GPS	embedded GPS	neighboring photos
Description	user assertion	embedded caption
Person	user decision	recognition model
Confidence

Confidence expresses how strongly the evidence supports a value.

Authority

Authority expresses who or what is allowed to establish the value.

A user decision can have high authority even when there is no machine-verifiable evidence.

An AI result can have high confidence but lower authority.

These concepts should remain separate.

# 17. Time Model

Capture time and filesystem timestamps are separate.

Capture Time

Describes when the photograph was taken.

It should support:

date/time
timezone
precision
Precision

Possible precision levels:

exact
minute
day
month
year
unknown

Bilder should not invent precision.

If only:

2013-07-14

is known, it should not silently become:

2013-07-14 00:00:00

as though midnight were known.

Filesystem Times

Filesystem timestamps belong to the file/version/source context.

Examples:

created
modified
imported

They are evidence but are not automatically the capture time.

# 18. Location

Location should distinguish raw geographic evidence from human-readable interpretation.

Coordinate

May contain:

latitude
longitude
coordinate precision
source
confidence
Human Location

May contain:

country
region
city
neighborhood
street
building / POI
Precision

Possible conceptual levels:

exact coordinate
building / POI
street
neighborhood
city
region
country
unknown

An inferred city should not automatically become an exact coordinate.

For example:

Probably Paris

is different from:

GPS: 48.8566, 2.3522

# 19. Metadata Correction Proposals

A metadata correction should normally be represented as a Proposal before becoming canonical.

Example:

Folder: The_America_Trip

Photos:
4132

Proposed:
Capture time -7 hours

Strong matches:
4118

Conflicts:
14

The UI may present this as one group operation.

The underlying data should remain individually auditable.

A user can:

approve all
approve only matching items
reject
inspect conflicts
edit individual values

# 20. FaceObservation

## Purpose

A FaceObservation represents one detected face in a media representation.

Possible information includes:

MediaFile/FileVersion analyzed
bounding box
detection confidence
landmarks
model/version
analysis time

A FaceObservation is not a person identity.

# 21. FaceCluster

## Purpose

A FaceCluster groups visually similar FaceObservations.

Clusters should initially be anonymous.

For example:

FaceCluster 42
├── FaceObservation A
├── FaceObservation B
├── FaceObservation C
└── FaceObservation D

The cluster does not need to be called:

Anna

until the user establishes that identity.

Cluster Changes

Clusters should support historical handling of:

split
merge
reassignment
rejected membership

This prevents destructive identity assumptions.

# 22. Person

A Person represents a user-defined real-world identity.

A Person may be linked to:

one or more FaceClusters
individual FaceObservations
Photos
identity decisions

A Person is not merely a tag.

# 23. IdentityProposal

Recognition systems may produce proposals.

Example:

FaceCluster 42

Anna      96%
Maria     71%
Unknown    4%

These values are machine evidence.

They do not establish identity automatically.

# 24. IdentityDecision

A user decision records acceptance or rejection of an identity proposal.

Possible decisions include:

confirm Anna
reject Anna
assign Maria
mark unknown
override cluster identity
split cluster
merge clusters

Historical decisions should remain available.

This specifically prevents the system from developing irreversible behavior where a mistaken assignment cannot be undone.

# 25. Tag

A Tag represents a structured characteristic or subject.

Possible categories include:

Person
Place
Event
Subject
Object
Activity
Organization
Custom

Tags should be separate entities rather than a comma-separated string.

Tag Provenance

A tag may originate from:

embedded metadata
user
AI proposal
external source

The origin matters.

An imported keyword is not equivalent to a user-confirmed tag.

# 26. Collection

A Collection is a logical grouping of Photos.

It answers:

Why do I want these Photos grouped?

A Collection may have:

name
description
date range
location
membership

A Photo can belong to multiple Collections.

Collections are independent of physical filesystem paths.

Collection Membership

Membership should be explicit and persistent.

It should not merely be a dynamically generated folder query.

# 27. Saved Search

A Saved Search is different from a Collection.

Collection
    = explicit membership

Saved Search
    = persistent query

The result of a Saved Search may change as the catalogue changes.

Examples:

Photos missing from NAS

Photos requiring time review

Previously deleted files found again

Photos with conflicting GPS

Files present only on old HDDs

# 28. Search Model

Search primarily operates on Photos.

This means:

3 physical copies

normally produce:

1 Photo search result

and:

Live Photo still + MP4

normally produces:

1 Photo result
Search Dimensions

Search may eventually support:

date/time
location
person
tags
description
collection
media type
file format
source
file state
preservation state

Physical-layer search is also important.

For example:

All files on HDD Backup 2019
that are not currently preserved on the NAS

The search model should be structured and reusable by:

web UI
API
CLI
future natural-language interface

A future LLM should translate natural-language requests into structured search criteria rather than directly manipulating database queries.

# 29. Operation

An Operation represents an attempted action.

Examples:

preserve file to NAS
move file
rename file
create quarantine copy
restore file
permanently delete file
synchronize metadata
apply timestamp correction
update identity

An Operation should eventually contain information such as:

operation type
target
requested by
requested at
started at
completed at
status
result
verification
error information

Operations should be resumable or reconcilable where practical.

# 30. Proposal

A Proposal represents a suggested change that has not yet been accepted.

Examples:

duplicate candidate
near-duplicate candidate
timestamp correction
GPS correction
face identity
metadata synchronization
quarantine candidate
collection suggestion

A Proposal is not an Operation.

The distinction is:

Proposal
    = Bilder recommends something

Decision
    = user decides what should happen

Operation
    = system performs the action

# 31. Decision

A Decision records an explicit human decision.

Examples:

Keep file
Delete file
Restore file
Reject duplicate
Confirm person
Reject person
Approve timestamp correction
Reject GPS proposal

Decisions should remain historically available.

They should not be silently replaced merely because an algorithm is updated.

# 32. Audit / Provenance

Bilder should preserve enough provenance to explain important catalogue state.

For a canonical value, it should eventually be possible to determine:

Current value
    ↓
Why was it selected?
    ↓
Which observations supported it?
    ↓
Which proposal was involved?
    ↓
Which decision established it?

For a file:

FileVersion
    ↓
Which scan discovered it?
    ↓
Which Source?
    ↓
Which path?
    ↓
When copied to NAS?
    ↓
Which verification?

For deletion:

FileVersion
    ↓
Why was it deleted?
    ↓
Which user decision?
    ↓
Which operation?
    ↓
Was deletion verified?

# 33. Relationships Overview

The conceptual relationships are:

Source
  │
  └── ScanSession
        │
        └── FileObservation
                │
                └── FileVersion
                        │
                        └── MediaFile
                                │
                                └── Photo

Physical copies:

FileVersion
   ├── SourceCopy ── Source
   ├── SourceCopy ── Source
   └── SourceCopy ── Source

Media relationships:

Photo
├── MediaFile
│     └── FileVersion
│
├── MediaFile
│     └── FileVersion
│
└── MediaFileRelationship

Metadata:

Photo
├── Canonical metadata
└── MetadataObservations

MediaFile / FileVersion
└── File-level observations

Faces:

Photo
└── FaceObservation
      └── FaceCluster
            └── Person

Logical organization:

Photo
├── Tags
├── Collections
└── People / Location

Decision workflow:

Observation
    ↓
Analysis
    ↓
Proposal
    ↓
Decision
    ↓
Operation
    ↓
Verification

# 34. File Discovery Lifecycle

A newly discovered file should conceptually pass through this process:

Physical file found
       ↓
FileObservation created
       ↓
Identify FileVersion
       ↓
Find existing SourceCopy?
       │
       ├── yes → known copy
       │
       └── no
            ↓
       Compare catalogue
            ↓
       Determine preservation state
            ↓
       ┌───────────────┬────────────────┐
       │               │                │
    preserved      needs NAS        previously
                     copy             deleted
       │               │                │
       │               ▼                ▼
       │          preserve          ask user
       │               │
       └───────────────┴───────┬────────┘
                               ↓
                           catalogue

Discovery itself does not modify the source.

# 35. Preservation Lifecycle

The preservation lifecycle is:

Discovered
    ↓
Compare
    ↓
Not preserved on NAS
    ↓
Preservation required
    ↓
Copy
    ↓
Verify
    ↓
NAS SourceCopy present

The system should distinguish:

copy attempted

from:

copy verified
36. Duplicate Lifecycle

Duplicate handling occurs after preservation.

Preserve
   ↓
Analyse
   ↓
Find exact / related / near-duplicate candidates
   ↓
User review
   ↓
Decision
   ↓
Quarantine if appropriate
   ↓
Waiting period
   ↓
Permanent deletion if explicitly approved

There is deliberately no relationship:

duplicate detected
        ↓
delete
# 37. Exact Duplicate Model

If two physical files have the same SHA-256:

File A SHA-256 = X
File B SHA-256 = X

then:

FileVersion X
├── SourceCopy A
└── SourceCopy B

They are not two FileVersions.

They are two physical copies.

# 38. Same Photo, Different Encoding

Example:

HEIC
JPG

They may decode to the same or nearly the same visual content.

The model should allow:

Photo X
├── MediaFile HEIC
└── MediaFile JPG

with:

HEIC ──alternate/derived── JPG

depending on what is known.

Bilder should not require exact proof of derivation before representing the possibility.

# 39. Same MediaFile, Different FileVersion

Example:

Original JPG
SHA-256 = A

Metadata is changed:

Modified JPG
SHA-256 = B

The model can represent:

Photo X
└── MediaFile JPG
      ├── FileVersion A
      └── FileVersion B

The FileVersions are different byte states of the same logical representation.

# 40. Database Authority

The database is authoritative for Bilder's interpretation.

The filesystem is authoritative for physical existence/location at the moment it is observed.

Embedded metadata is evidence and a synchronization mechanism.

This gives three different roles:

Database
    = What Bilder believes

Filesystem
    = What physically exists

Embedded metadata
    = What the file itself says

Disagreements between these layers should be visible rather than silently hidden.

# 41. Physical vs. Logical Organization

The data model must not encode the NAS directory structure as the logical organization of Photos.

For example:

2026/
└── 08-23_Concert/
    └── IMG_1234.HEIC

is physical context.

The same Photo may logically have:

Person:
Anna

Location:
Berlin

Tags:
Concert
Music

Collections:
Summer 2026
Concerts

The physical file should not need to be duplicated into those logical categories.

# 42. Important Invariants

The implementation should preserve these invariants.

Identity

A Photo represents one real-world capture.

Exact File Identity

A FileVersion represents one exact byte sequence.

Physical Copy

A SourceCopy represents one physical occurrence of a FileVersion.

Exact Duplicate

Same SHA-256 means the same FileVersion.

Preservation

Every discovered photographic file should exist at least once on the NAS unless explicitly deleted and documented.

Discovery

Scanning does not silently modify sources.

Deletion

Permanent deletion requires explicit authorization.

History

Important observations and decisions should not be silently overwritten.

User Authority

User decisions override machine proposals.

Logical Organization

Tags and Collections do not determine physical filesystem location.

Search

Normal photo search returns logical Photos rather than duplicate physical copies.

# 43. Deferred Implementation Details

The following should be designed after the conceptual model is agreed:

SQLite table names
exact columns
primary key strategy
UUID vs integer IDs
foreign keys
indexes
enum implementation
JSON usage
migration strategy
job queue implementation
filesystem locking
transaction boundaries
thumbnail storage
binary metadata storage
retention policy for observations
API representation
authentication implementation

These are implementation decisions, not part of the conceptual identity model.

# 44. Initial Entity Checklist

The initial conceptual entity set is:

Core
Photo
MediaFile
MediaFileRelationship
FileVersion
Source
SourceCopy
Discovery
ScanSession
FileObservation
Metadata
MetadataObservation
canonical Photo metadata
Location
canonical Location
location observations/proposals
Faces
FaceObservation
FaceCluster
Person
IdentityProposal
IdentityDecision
Organization
Tag
Photo–Tag relationship
Collection
Collection membership
SavedSearch
Operations
Proposal
Decision
Operation
operation results / verification
History
audit/provenance information

This list is conceptual. Some entities may later be represented as relationships, state tables, or other implementation structures rather than literal SQLite tables.

# 45. Intended Evolution

The data model should evolve in this order:

Conceptual entities
       ↓
Relationships
       ↓
State transitions
       ↓
SQLite schema
       ↓
Migrations
       ↓
Application services
       ↓
API
       ↓
Web UI

The database schema should not be designed first and then used to define the concepts.

The concepts should define the schema.

# 46. Summary

The central model is:

                         Source
                           │
                           │
                      SourceCopy
                           │
                           │
                      FileVersion
                           │
                           │
                       MediaFile
                           │
                           │
                         Photo
                      /    │    \
                     /     │     \
                 Faces    Tags   Collections
                   │
              FaceCluster
                   │
                Person

With discovery:

Source
  ↓
ScanSession
  ↓
FileObservation
  ↓
FileVersion
  ↓
MediaFile
  ↓
Photo

And controlled change:

Observation
    ↓
Analysis
    ↓
Proposal
    ↓
User Decision
    ↓
Operation
    ↓
Verification

The most important architectural distinction is:

A photograph, a representation of that photograph, the exact bytes of that representation, and a physical copy of those bytes are four different things.

This separation allows Bilder to preserve the archive first, understand duplicates later, retain historical evidence, support multiple sources, and make potentially destructive changes reversible and auditable.


These two files are deliberately **conceptual rather than schema-heavy**. I think that's the right point to stop before we start designing SQLite tables—especially because the `Photo → MediaFile → FileVersion → SourceCopy → Source` distinction is now the foundation everything else can build on.



























