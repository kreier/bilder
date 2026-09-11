# Bilder — Phase 2A Decision Matrix

**Status:** Archived  
**Phase:** 2A — Architecture and Data Model  
**Decision date:** 2026-09-11

> This document preserves the architectural design discussion that preceded the Phase 2A freeze. It contains a condensed record of the 178 questions and decisions discussed during that process.
>
> It is intentionally more detailed than the current architecture documentation. It records **what was considered and decided**, including decisions that were later classified as implementation details.
>
> The current source of truth is:
>
> - `docs/architecture.md`
> - `docs/data-model.md`
> - `docs/configuration.md`

---

## Decision matrix

| # | Area | Decision | Result / consequence |
|---:|---|---|---|
| 1 | Identity | Physical file and logical Photo are separate concepts | One physical file maps to one File; Photo identity is independent |
| 2 | Identity | Multiple files may represent one Photo | RAW, JPEG, copies and alternate representations can share a Photo |
| 3 | Identity | Identical physical files remain separate Files | Same SHA-256 does not eliminate separate physical File records |
| 4 | Identity | Move/rename preserves identity | Path is mutable metadata, not identity |
| 5 | Identity | Metadata changes do not normally create a new Photo or File | Logical identity survives metadata changes |
| 6 | Identity | EXIF/metadata changes can change file bytes without changing Photo | A new FileVersion records the changed bytes |
| 7 | Identity | Rotation/orientation changes preserve Photo identity | Orientation is normalized for comparison |
| 8 | Identity | Minor visual corrections preserve Photo identity | Exposure, contrast, sharpening, noise reduction etc. remain same Photo |
| 9 | Identity | Cropping creates a new Photo | Crop is a substantive compositional change |
| 10 | Identity | Substantive resizing creates a new Photo | Trivial technical changes may remain same Photo |
| 11 | Identity | Major editing creates a new Photo | Object removal, compositing, background replacement and major retouching create derivatives |
| 12 | Provenance | Derived Photos have explicit source relationships | Transformation provenance is recorded |
| 13 | Identity | Deleted source files do not delete Photo history | Logical Photo remains historically available |
| 14 | Identity | Different encodings may represent the same Photo | JPEG/PNG/RAW can share Photo identity |
| 15 | Pairing | RAW+JPEG pairing is attempted automatically when evidence is strong | Ambiguous pairing remains separate for review |
| 16 | File identity | Same tracked path with changed content retains File identity | New FileVersion represents changed physical content |
| 17 | File history | File versions are retained | Previous content and associations remain auditable |
| 18 | Metadata | Metadata byte changes create FileVersions | EXIF modifications become historical states |
| 19 | Visual identity | Deterministic visual identity may eventually be used | Comparison can normalize orientation/dimensions/pixels |
| 20 | Visual identity | Similarity alone cannot establish identity | Automatic merging requires multiple strong signals |
| 21 | Human decisions | Manual identity decisions are recorded | Human decisions become part of provenance |
| 22 | Human decisions | Manual identity decisions are reversible | Incorrect decisions can be undone |
| 23 | Originals | No File is inherently required to be the "original" | The model does not impose a mandatory original representation |
| 24 | Derivatives | Derived Photos may have multiple Files | A derivative can have RAW/JPEG/etc. representations |
| 25 | Provenance | Derivation chains are supported | A derivative may itself become the source of another derivative |
| 26 | Provenance | Multiple parents are supported | Composites can derive from multiple Photos |
| 27 | Provenance | Deleted derivatives remain in historical provenance | Normal deletion does not erase derivation history |
| 28 | Purge | Permanent deletion is a separate explicit operation | Normal deletion retains history |
| 29 | IDs | Photo IDs are opaque | No semantic meaning is encoded in Photo IDs |
| 30 | IDs | File IDs are opaque | No semantic meaning is encoded in File IDs |
| 31 | Rebuild | Full database rebuild may generate new IDs | Stable IDs are guaranteed for normal operation, not arbitrary total rebuilds |
| 32 | Rescan | Normal rescans preserve identities | Matching uses path first, then stronger identity evidence |
| 33 | Moves | Moved/renamed files are detected when evidence permits | Existing File identity is restored |
| 34 | Copies | A copied physical file gets its own File ID | It may still reference the same Photo |
| 35 | Deletion | Removing one copy does not remove the Photo | Photo remains active while another File exists |
| 36 | Photo state | A Photo with no Files is retained as missing | Missing is distinct from historical deletion |
| 37 | Reappearance | A confidently reidentified Photo restores its Photo ID | History is preserved across temporary absence |
| 38 | File reappearance | A returning identical physical file restores its File ID | Previous path/history remains available |
| 39 | Path identity | Same path does not prove same physical file | Path alone is insufficient after replacement |
| 40 | Replacement | In-place replacement retains File history | New FileVersion may point to another Photo |
| 41 | Hashing | Every FileVersion has content-hash information | Physical byte identity can be established |
| 42 | Hashing | SHA-256 is used | Authoritative exact-content hash |
| 43 | Hashing | Hashing occurs during scanning when required | Scanner establishes content identity |
| 44 | Optimization | Path + size + mtime can provide a fast unchanged path | Avoid unnecessary hashing |
| 45 | Optimization | Trust in mtime is configurable | Scanner can use conservative or optimized behavior |
| 46 | Hashing | Hash algorithm is recorded | Stored hashes remain interpretable |
| 47 | Optimization | Fast fingerprints may be supported | Potential optimization separate from authoritative hash |
| 48 | Optimization | Fast fingerprints are deferred from Phase 2 | Not required for initial architecture |
| 49 | Hashing | Hashes are evidence, not universal identity | Same hash does not define logical Photo identity |
| 50 | Duplicates | Exact duplicate content can be associated with one Photo | Shared SHA-256 provides strong evidence |
| 51 | Conflicts | Same SHA-256 under different Photo IDs is a conflict | Do not automatically merge; flag for review |
| 52 | Duplicates | Exact duplicate copies retain separate File IDs | Physical copies remain independently trackable |
| 53 | Duplicates | No mandatory duplicate junction table | Exact duplicates can be derived from hashes |
| 54 | Scanner errors | Hashing errors are recorded | Scanner does not silently discard failures |
| 55 | Scanner errors | Retryable errors are supported conceptually | Temporary failures can be retried |
| 56 | Scanner errors | Error history is retained | Audit trail explains incomplete operations |
| 57 | Scans | Scans have persistent ScanRun records | Every catalog scan is auditable |
| 58 | Roots | Multiple scan roots are supported | Independent filesystem trees can be cataloged |
| 59 | Roots | Unavailable roots remain known | A missing disk is not treated as an empty root |
| 60 | Missing detection | Missing detection requires successful observation | Incomplete scans cannot cause mass false deletions |
| 61 | Roots | Scan results are recorded per root | Overall status can be derived from root outcomes |
| 62 | Scans | Selective root scans are supported | Users can scan specific roots |
| 63 | Discovery | Recursive scanning is supported | Directory trees can be traversed |
| 64 | Symlinks | Symlinks are not followed by default | Prevent unintended traversal/duplication |
| 65 | Discovery | Hidden/system files are discoverable when supported | Hidden status is not automatically an exclusion |
| 66 | Exclusions | Configurable exclusion patterns are supported | Unwanted paths can be excluded deterministically |
| 67 | Exclusions | Exclusion changes retain history | Previously discovered objects are not forgotten |
| 68 | Exclusions | Re-inclusion restores previous identity when possible | Excluding a file does not destroy its history |
| 69 | File types | Supported file types are configurable | Scanner behavior is configuration-driven |
| 70 | Extensions | Extension matching is case-insensitive | `.JPG` and `.jpg` are equivalent for discovery |
| 71 | File types | Extension alone is insufficient | Contents are verified after extension-based discovery |
| 72 | Metadata | Technical metadata is extracted | Camera, dimensions, dates, GPS etc. can become observations |
| 73 | Metadata | Metadata history is retained | Changed observations remain auditable |
| 74 | Provenance | Metadata source is recorded | Extracted, manual and AI-derived values remain distinguishable |
| 75 | Metadata | Manual metadata is supported | Users can provide authoritative catalog information |
| 76 | Conflicts | Manual metadata wins current effective value | Extracted conflicting observations remain preserved |
| 77 | Source safety | Source files are never modified automatically | Catalog operation is non-destructive |
| 78 | Sidecars | Automatic sidecar creation is disabled | Metadata stays in catalog unless user explicitly exports/writes it |
| 79 | Provenance | Individual metadata values have provenance | Effective values can be traced to their source |
| 80 | Conflicts | Competing metadata values are preserved | Conflicts are not silently discarded |
| 81 | AI metadata | Inferred/suggested values have confidence | Machine suggestions remain distinguishable from facts |
| 82 | Confidence | Confidence uses 0.0–1.0 | Standard numeric representation |
| 83 | Confidence | Confidence means likelihood of correctness | Source reliability is a separate concept |
| 84 | Automation | Automatic acceptance thresholds are configurable | Machine suggestions can be promoted according to policy |
| 85 | Automation | Thresholds may be field-specific | Different metadata types can require different confidence |
| 86 | History | Confidence changes are historical | Previous suggestions/acceptance decisions remain auditable |
| 87 | Evidence | Confidence requires supporting evidence | A number without explanation is insufficient |
| 88 | Evidence | Evidence is structured | Machine reasoning can be inspected |
| 89 | Evidence | Evidence is immutable | Historical evidence cannot silently change |
| 90 | Reproducibility | Rules/algorithm versions are recorded | Decisions can be interpreted in historical context |
| 91 | Reproducibility | Software version is recorded | Scanner/analysis behavior is attributable |
| 92 | Reproducibility | Configuration version is recorded | Behavior is tied to configuration |
| 93 | Reproducibility | Configuration snapshots are stored | Historical scans can be reconstructed conceptually |
| 94 | Configuration | Snapshots use canonical JSON | Equivalent configurations have deterministic representation |
| 95 | Configuration | Configuration has SHA-256 | Snapshot identity can be checked |
| 96 | Scanning | Scan behavior should be reproducible | Same inputs/configuration should lead to equivalent catalog decisions |
| 97 | Scans | ScanRun IDs are opaque | Scan IDs carry no semantic meaning |
| 98 | Audit | File-level scan events are recorded | Important discovery/change outcomes are explainable |
| 99 | Audit | Events record reason/evidence | Historical decisions are interpretable |
| 100 | Audit | Event history is retained indefinitely under normal operation | History is not routinely discarded |
| 101 | Audit | Events are append-only | Existing historical events are not rewritten |
| 102 | Audit | Event payloads use canonical JSON where structured | Event representation is deterministic |
| 103 | Audit | Events identify actor | Scanner, manual, import, AI and system actions are distinguishable |
| 104 | Audit | Events have timestamps | Temporal ordering is available |
| 105 | Audit | Events have sequence numbers | Deterministic event ordering is possible |
| 106 | Audit | Only meaningful outcomes become events | Internal implementation steps need not pollute the audit trail |
| 107 | Audit | Root-level events exist | Root availability/failure/completion is auditable |
| 108 | Scan status | Overall success requires all selected roots to succeed | Mixed root results produce partial status |
| 109 | Scan status | Empty root can be successful | Empty directories are valid successful observations |
| 110 | Roots | Scan roots have persistent identity | A root remains identifiable across scans |
| 111 | Roots | Root path history is retained | Root changes are auditable |
| 112 | Roots | Root configuration history is retained | Scanner behavior over time is explainable |
| 113 | Roots | Roots have labels | Human-readable names are supported |
| 114 | Roots | Roots have enabled/disabled state | Operational state is separate from reproducibility |
| 115 | Roots | Disabled roots are skipped | They produce no missing/unavailable events |
| 116 | Roots | Last scan is tracked per root | Current root status can be inspected |
| 117 | Roots | Root scan timestamps are recorded | Scan chronology is available |
| 118 | Concurrency | Same root cannot be scanned concurrently | Prevent conflicting observations |
| 119 | Concurrency | Different roots may be processed concurrently | Allows implementation parallelism |
| 120 | Concurrency | One overall catalog scan run at a time | Global scan ownership is explicit |
| 121 | Scans | Cancellation is supported | Long-running scans can stop safely |
| 122 | Cancellation | Cancelled scans perform no missing detection | Prevent false disappearance |
| 123 | Transactions | Scan completion is atomic | Final missing-state transition happens only after successful completion |
| 124 | Transactions | File processing may commit incrementally | Final completion/missing transition remains protected |
| 125 | Recovery | Crashed scans are recoverable | Application can identify abandoned work |
| 126 | Recovery | Abandoned scans are recovered at startup | Stale running states do not persist forever |
| 127 | Recovery | Scan heartbeat exists | Running ownership can be monitored |
| 128 | Recovery | Heartbeat timeout is configurable | Operational tuning remains possible |
| 129 | Recovery | Stale scan ownership can be detected | Another run can eventually recover |
| 130 | Recovery | Scan ownership uses a token | Prevents accidental ownership takeover |
| 131 | Scan status | Overall statuses are fixed conceptually | `running`, `successful`, `partial`, `cancelled`, `failed`, `aborted` |
| 132 | Scan status | `partial` means incomplete but meaningful results exist | Root failures/unavailability can produce partial |
| 133 | Root status | Root statuses are fixed conceptually | `pending`, `running`, `successful`, `unavailable`, `failed`, `cancelled`, `skipped` |
| 134 | Root status | `skipped` means intentionally not processed | Different from failure |
| 135 | Cancellation | Root cancellation contributes to incomplete scan | Overall scan cannot become successful |
| 136 | Failure | Failed root produces overall partial status | Unless all selected roots fail |
| 137 | Failure | All roots failing produces overall failed status | No useful successful root observation exists |
| 138 | Empty scope | Zero selected roots is successful no-op | No work is a valid successful scan |
| 139 | Audit | Scan scope is recorded | Later inspection knows what was requested |
| 140 | Configuration | Per-root configuration snapshot is recorded | Each root's scan behavior is reconstructable |
| 141 | Configuration | Root configuration has hash | Configuration identity is checkable |
| 142 | Configuration | Root configuration has version | Changes can be tracked chronologically |
| 143 | Configuration | Version changes only when effective behavior changes | Presentation-only changes do not create versions |
| 144 | Configuration | Root labels are excluded from reproducibility identity | Labels are presentation metadata |
| 145 | Configuration | Enabled state is excluded from reproducibility identity | Operational state is not scanner behavior |
| 146 | Configuration | Root path is part of reproducibility configuration | It changes what filesystem is observed |
| 147 | Configuration | Exclusions are part of configuration | They directly affect discovery |
| 148 | Configuration | Supported extensions are part of configuration | They affect discovery |
| 149 | Configuration | Recursive setting is part of configuration | It affects discovery scope |
| 150 | Configuration | Symlink policy is part of configuration | It affects discovery |
| 151 | Determinism | File discovery order is deterministic | Results are not dependent on filesystem iteration order |
| 152 | Parallelism | File processing may be parallel | Event ordering follows deterministic discovery order |
| 153 | Performance | Exact concurrency limits are not architecture | Defer worker/resource tuning |
| 154 | Performance | Exact worker count is not frozen | Implementation can choose appropriate strategy |
| 155 | Performance | CPU limits are not architecture | Tune after real measurements |
| 156 | Performance | Memory limits are not architecture | Tune after implementation |
| 157 | Performance | Queue sizing is not architecture | Defer until scanner implementation |
| 158 | Performance | Back-pressure policy is not architecture | Implementation concern |
| 159 | Performance | Batch sizes are not architecture | Tune empirically |
| 160 | Performance | Hardware-specific optimization is deferred | Avoid premature constraints |
| 161 | Performance | Benchmarking should precede optimization | Measure actual workload first |
| 162 | Model | Photo, File and FileVersion are distinct | They must not be collapsed into one entity |
| 163 | Relationship | Photo → File is one-to-many | No Photo/File many-to-many junction table |
| 164 | Lifecycle | Photo may exist without File | Missing Photo history is valid |
| 165 | Findings | Normal cataloged Files always belong to a Photo | Unclassified relevant objects use Finding instead |
| 166 | Findings | Findings are persistent | Discovery uncertainty is historical data |
| 167 | Findings | Findings can be classified later | Classification becomes part of provenance |
| 168 | Findings | Only potentially relevant objects become Findings | Ordinary unrelated filesystem objects remain ignored |
| 169 | Findings | Candidate file types are configurable | Potential relevance is configuration-driven |
| 170 | Findings | Missing Findings remain in database | Temporary disappearance does not destroy history |
| 171 | Findings | Reappearing Findings restore identity when confidently matched | Finding history survives disappearance |
| 172 | Findings | Classification creates a normal File while preserving Finding history | Original uncertainty remains auditable |
| 173 | Findings | Classification is reversible | A File can return to unassociated state |
| 174 | Findings | Returning Findings can be matched using path/history then stronger evidence | SHA-256 and other evidence can improve confidence |
| 175 | Findings | Finding content history was considered | Historical content changes should eventually be representable |
| 176 | Findings | Finding technical metadata can be historical | Metadata may need version association |
| 177 | Findings | Metadata changes can create Finding versions | Exact implementation deferred |
| 178 | Findings | Finding versions may have opaque IDs | Recorded as a historical decision, but detailed schema deferred |

---

# Decision categories

The 178 decisions can be grouped into the following architectural areas:

| Category | Decisions |
|---|---:|
| Photo / File identity | 1–40 |
| Hashing / duplicate detection | 41–56 |
| Scanning / roots / discovery | 57–73 |
| Metadata / provenance | 74–95 |
| Scan audit / lifecycle | 96–117 |
| Scan concurrency / recovery | 118–138 |
| Configuration / determinism | 139–152 |
| Performance decisions deliberately deferred | 153–161 |
| Findings / entity relationships | 162–178 |

---

# Decisions that are architectural vs. deferred

Not every answer in the original discussion has equal architectural weight.

## Frozen architectural decisions

The following are part of the Phase 2A architecture:

- Photo/File/FileVersion/ Finding separation
- Photo identity rules
- File identity and versioning
- SHA-256 as exact byte identity
- conservative identity matching
- provenance
- derivation relationships
- deletion/missing semantics
- scan roots
- safe missing detection
- scan history and audit events
- reproducibility
- deterministic discovery
- configuration snapshots
- persistent Findings
- reversible classification
- non-destructive source-file policy

## Deliberately deferred

The following were discussed but are not intended to constrain implementation prematurely:

- exact worker counts
- CPU/memory limits
- queue sizes
- batch sizes
- fast fingerprints
- exact Finding-version schema
- exact metadata schema
- exact confidence thresholds
- advanced visual matching
- purge implementation
- detailed UI behavior
- AI implementation

These may become architectural decisions later if implementation reveals a genuine conflict.

---

# Final architectural principles

The detailed discussion ultimately established these twelve principles:

1. **Photo, File, FileVersion and Finding are distinct concepts.**
2. **Photo identity is logical; File identity represents physical-file history.**
3. **Paths and filenames are attributes, never identities.**
4. **Photos may have multiple representations and may temporarily have none.**
5. **FileVersions preserve physical-file history.**
6. **Substantive transformations create derived Photos according to conservative identity rules.**
7. **Provenance is first-class and human decisions are reversible.**
8. **SHA-256 establishes byte identity but does not define Photo identity.**
9. **The database is the authoritative catalog; source files are never modified automatically.**
10. **Scanning is deterministic, auditable, reproducible and safe against incomplete observations.**
11. **Potentially relevant but unclassified filesystem objects persist as Findings.**
12. **Implementation details are deferred until they are justified by actual requirements or measurements.**

---

# Relationship to current documentation

This decision matrix is historical documentation.

The current implementation contract is defined by:

```text id="2yl4v5"
docs/architecture.md
docs/data-model.md
docs/configuration.md
```

If a future implementation question appears to contradict this archive, the current documentation takes precedence.

The purpose of this file is different:

> **The current docs explain what we decided.  
> This archive records the decisions that led us there.**