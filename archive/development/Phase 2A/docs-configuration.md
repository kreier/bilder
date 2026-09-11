# Bilder — Configuration

## Status

**Phase 2A configuration contract frozen — 2026-09-11**

This document defines which configuration concepts affect scanner reproducibility. It intentionally does not prescribe the final configuration-file syntax or every future application setting.

## 1. Configuration principles

Configuration is divided conceptually into:

1. **Reproducibility configuration** — settings that can change what a scan discovers or how it interprets a root.
2. **Presentation/operational state** — settings that affect how the application operates or displays information but do not change the meaning of a completed scan.

Only the first category participates in the root configuration version/hash.

## 2. Scan root configuration

Each ScanRoot has an opaque stable `root_id`.

The reproducibility configuration includes:

### Filesystem path

The current path of the root.

Changing the path creates a new root configuration version.

The path is configuration, not root identity.

### Include/exclude patterns

Patterns determining which paths are scanned or ignored.

Changes create a new root configuration version.

Excluded cataloged files remain historical records and may become active again if the exclusion is removed.

### Supported extensions

The configured list of candidate photo/media extensions.

Extension matching is case-insensitive.

The list is part of reproducibility configuration.

### Recursive scanning

Whether subdirectories are scanned.

This is part of reproducibility configuration.

### Symlink policy

The scanner does not follow symbolic links by default.

The configured symlink policy is part of reproducibility configuration.

### Candidate-file configuration

The scanner may retain potentially relevant but unclassified filesystem objects as Findings.

The rules determining which objects qualify as candidates are part of reproducibility configuration.

## 3. Configuration versioning

Each ScanRoot has a monotonically increasing configuration version.

A new version is created only when effective reproducibility configuration changes.

The effective configuration is stored as a canonical JSON snapshot.

A SHA-256 hash of that canonical representation identifies the exact configuration used.

A scan records the configuration snapshot/hash that was active when the root was scanned.

## 4. Settings that do not change root configuration identity

The following are not part of reproducibility configuration:

- human-readable root label
- enabled/disabled state

Disabling a root changes whether it is included in a scan, but does not change the root's configuration identity.

A disabled root is skipped by normal full scans and does not generate missing/unavailable consequences merely because it is disabled.

## 5. Global scanner configuration

The application may also have global settings such as:

- software version
- scanner implementation version
- metadata extractor version
- supported processing rules
- timezone/default interpretation settings
- future analysis settings

The exact division between global and root-specific configuration is an implementation concern.

Whenever a setting can materially affect scanner results, the relevant scan must retain enough configuration context to reproduce the result.

## 6. Scan scope

Every ScanRun records exactly which roots were selected.

A selective scan therefore does not affect roots that were not selected.

A disabled or omitted root is not treated as missing.

A scan with zero selected roots is a valid no-op successful run.

## 7. Missing-file safety

Missing detection is allowed only when the scanner has sufficient evidence that a selected root was completely scanned.

The following must not cause files to become missing automatically:

- root unavailable
- permission failure
- network interruption
- scanner crash
- cancellation
- incomplete scan
- inaccessible directory that prevents complete discovery

The overall scan must therefore distinguish successful completion from partial/incomplete execution.

## 8. Scanner optimization

The architecture permits optimization such as:

```text
known path + size + mtime
        ↓
unchanged?
   yes → reuse known SHA-256
   no  → calculate SHA-256
```

Size and filesystem timestamps are optimization signals only.

They are never authoritative file identity.

The default behavior must favor correctness when filesystem metadata is uncertain.

Fast fingerprints may be introduced later as an optimization, but they are explicitly outside the Phase 2A contract.

## 9. Deterministic discovery

Within a root, discovery uses a deterministic ordering, such as lexicographically sorted relative paths.

Files may eventually be processed in parallel.

Parallel completion order must not determine historical event sequence.

This allows implementation optimization without sacrificing reproducibility.

## 10. Scan configuration snapshot

Each ScanRun should retain:

- Bilder/software version
- effective global settings relevant to the scan
- selected roots
- root configuration version
- canonical configuration snapshot
- configuration SHA-256

This allows later investigation of why a scanner produced a particular result.

## 11. Configuration changes and history

Configuration changes are historical facts.

The system should be able to answer:

> Which configuration was active when this file was discovered?

and:

> Why did the scanner behave differently after a configuration change?

Old configuration snapshots therefore remain available as historical scan context.

## 12. Deferred configuration decisions

The following are intentionally not frozen:

- exact YAML/TOML/JSON configuration-file format
- default confidence thresholds
- worker counts
- CPU/memory limits
- cache settings
- database connection settings
- exact UI settings
- fast fingerprint parameters
- AI model configuration
- purge/retention policy details
- total database rebuild strategy

These can be introduced when their implementation need becomes concrete.

## 13. Phase 2 implementation sequence

The intended sequence is:

1. Freeze this conceptual configuration contract.
2. Implement the SQLite representation.
3. Build the Database Inspector.
4. Use real catalog data to validate the configuration model.
5. Implement the deterministic Phase 2B scanner.
6. Add later analysis and automation without weakening reproducibility.