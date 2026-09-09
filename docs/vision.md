# Bilder — Vision

## Purpose

Bilder is intended to become a self-hosted, long-term photo archive and management system.

Its purpose is to provide a reliable catalog and management layer for a large personal photo collection while keeping the original files under the user's control.

The system should make it possible to:

- find and browse photos through a central catalog
- preserve original files without unnecessary modification
- understand where every photo and file version came from
- identify exact duplicates and visually similar photos
- collect and preserve useful metadata
- maintain thumbnails and previews for efficient browsing
- connect multiple photo sources without treating them all as equal
- safely manage duplicate copies in external services
- recover meaningful information even if the application database is lost
- perform potentially destructive operations only with explicit user approval

Bilder is intended to be a **self-hosted system**, not a cloud photo service.

## Canonical Archive

The NAS is the intended canonical storage location for the photo collection.

The canonical archive should contain the files that the user considers part of the long-term collection. The Bilder application does not replace the NAS as the underlying storage system; it provides the catalog, metadata, analysis, and management layer around it.

Other locations may contain copies of the same photographs. These are treated as external sources rather than automatically becoming part of the canonical archive.

Examples include:

- Apple Photos and iCloud Photos
- Google Drive
- phone backups
- camera memory cards
- exported photo collections
- other filesystem locations

A copy existing in an external source does not by itself mean that it should be deleted.

## Photo Identity

Bilder distinguishes between a **logical photographic capture** and its **physical media representations**.

A logical photographic capture has a stable `photo_id`. This identifier represents the capture or photographic event as an entity within Bilder and should remain stable across different file versions and related media representations.

A single `photo_id` may therefore correspond to more than one media file. For example, an iPhone Live Photo may consist of a still image and a short companion video, while a RAW capture may have both its original RAW file and a derived JPEG. These files are related representations of the same capture rather than necessarily being separate photographs.

The relationships between related media should be explicit. Examples include:

- `companion` — such as a Live Photo still and its motion video
- `derived` — such as a JPEG rendered from a RAW file
- `edited` — a modified representation of the same capture
- `alternate` — another representation of the same capture

The exact database model for these relationships is intentionally deferred to the data-model design stage.

A physical file is represented separately from the logical photograph. A particular stored state of that file has its own file identity and SHA-256 hash, which identifies its exact byte content.

This distinction is important because the same capture may exist as:

- an untouched original
- a copy with different metadata
- a resized version
- a recompressed version
- an edited version
- a derived representation
- a companion media file
- a file exported from another application

These files may have different SHA-256 hashes while still belonging to the same logical photographic capture.

Visual similarity mechanisms such as perceptual hashing (`pHash`) may be used to help identify these relationships.

External systems may also have their own identifiers. For example, an Apple Photos asset can have an Apple/iCloud identifier. Such identifiers belong to the source system and are not substitutes for Bilder's own `photo_id`.

## Provenance and History

Bilder should preserve the history of files rather than treating every file as an isolated object.

For each file version, the system should be able to record information such as:

- where it came from
- when it was discovered
- its exact content hash
- relevant metadata
- which logical photographic capture it belongs to
- whether it is canonical or an external copy
- relationships to other media and versions
- operations performed on it

This allows Bilder to answer questions such as:

> Where did this file come from?

> Which copies of this photograph exist?

> Which version is currently canonical?

> What changed between two versions?

> Can this photograph still be identified if one source disappears?

## Metadata

Bilder should make useful photo metadata searchable without unnecessarily changing the original files.

Potential metadata includes:

- capture date and time
- camera and lens information
- image dimensions
- orientation
- GPS information
- software and processing information
- file timestamps
- embedded metadata such as EXIF and XMP

The **database is the authoritative metadata catalog** for Bilder. Embedded metadata is an optional synchronization and portability mechanism, and its capabilities depend on the file format. Different formats may support different metadata mechanisms, so Bilder must not depend on every file being able to store the same information.

The system should distinguish metadata belonging to the original file from metadata generated or maintained by Bilder.

Where appropriate, Bilder may eventually embed its own stable identifier into a canonical file's metadata. Such a modification creates a new physical file version and therefore a new SHA-256 hash; it does not change the logical `photo_id`.

The original file should initially be preserved bit-for-bit whenever possible.

## Duplicate Detection

Duplicate detection is an important function, but it should not automatically imply deletion.

Bilder should distinguish at least between:

- exact file duplicates
- likely copies with different metadata
- resized or recompressed copies
- visually similar photographs
- edited versions
- photographs that are merely similar but not duplicates

Detection should produce information and recommendations.

The user remains responsible for deciding what should be retained or removed.

## Safe Operations

Bilder should be conservative when modifying or deleting data.

Potentially destructive operations should follow a workflow similar to:

1. Discover
2. Compare
3. Recommend
4. Request user approval
5. Quarantine
6. Verify
7. Permanently delete only when explicitly requested

Permanent deletion should never be the default consequence of duplicate detection.

Where possible, operations should be reversible and recorded in an audit history.

## External Sources

Bilder should be able to understand multiple sources without requiring them to become part of the canonical archive.

A source can contain:

- original files
- copies of canonical files
- edited versions
- resized versions
- files with modified metadata
- files that do not exist in the canonical archive

The system should therefore model the relationship between a photographic capture and its copies across sources.

This is particularly important for Apple Photos/iCloud Photos and Google Drive, where copies may exist independently of the NAS archive.

## Apple Photos and iCloud

Apple Photos is a special source because access to the user's Photos library is controlled by Apple's PhotoKit framework.

The intended architecture therefore uses a macOS application as a bridge:

**Bilder Server → macOS Bilder Bridge → PhotoKit → Apple Photos / iCloud Photos**

The Raspberry Pi should not attempt to reverse-engineer Apple's private Photos/iCloud protocols.

The macOS bridge is responsible for interacting with the Photos library and communicating the relevant information to the Bilder server.

## Resilience

The photo archive should remain understandable even if individual system components fail.

In particular:

- the NAS should remain usable independently of the Bilder application
- original files should not depend exclusively on the database
- file identity should be recoverable where practical
- important relationships should be represented in durable metadata where appropriate
- the database should be backed up independently
- operations should have a history that can be audited

The goal is that losing the application or database should be inconvenient, but should not make the underlying photo collection unusable.

## Privacy

The photo collection is private personal data.

The public GitHub repository may contain:

- source code
- documentation
- database schemas
- migrations
- synthetic test data
- sanitized examples
- carefully reviewed aggregate statistics

It must not contain:

- actual photographs
- personal photo metadata
- GPS coordinates
- real filenames or private filesystem paths
- cloud asset identifiers
- personal database records
- authentication credentials
- API tokens
- private network information

The repository should remain useful as a public software project without exposing the private photo collection.

## Development Principles

Bilder should be developed incrementally.

The architecture describes the intended destination, but not every component described here needs to exist immediately.

Development should favor:

- small, understandable changes
- explicit design decisions
- simple components
- testable functionality
- read-only operation before modification
- reversible operations
- minimal dependencies
- clear separation between discovery and destructive actions
- privacy by default

The system should be built in stages, validating each layer before adding the next.

## Long-Term Goal

The long-term goal is a single, trustworthy catalog of the user's photographs, independent of where copies happen to exist.

The user should be able to open Bilder and understand:

- what photographs exist
- where their files are stored
- which copies exist elsewhere
- which versions are originals or derivatives
- what metadata is available
- which photographs are duplicates or near-duplicates
- what actions have been performed
- what can safely be changed or removed

The NAS remains the foundation of the archive.

Bilder provides the intelligence, catalog, history, and user interface around it.