# My proposed sequence from here

I'd proceed roughly like this:

## Phase 1 — Model validation

**Now**

1. architecture.md ✅
2. data-model.md ✅
3. Define implementation boundary
4. Define initial SQLite schema
5. Build a tiny scanner
6. Test against representative files

## Phase 2 — Catalogue

Then:

```text
Source
ScanSession
FileObservation
FileVersion
MediaFile
Photo
SourceCopy
```

with repeatable scans.

At this point Bilder becomes genuinely useful even without a UI.

## Phase 3 — Metadata

Add:

```text
MetadataObservation
Canonical metadata
```

and extract EXIF/XMP/filesystem metadata.

## Phase 4 — Preservation

Only then implement:

```test
NAS preservation
quarantine
previously-deleted detection
restore workflow
```

This is where your **"maximum number of pictures on the NAS first"** principle becomes operational.

## Phase 5 — Search

Once the catalogue contains real data:

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

## Phase 6 — Advanced analysis

Only after the deterministic foundation works:

```text
pHash
pixel similarity
faces
clustering
AI proposals
metadata correction proposals
discovery
```
