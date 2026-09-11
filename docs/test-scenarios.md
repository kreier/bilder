# Bilder — Test Datasets & Validation Scenarios

**Status:** Active  
**Purpose:** Specification of synthetic test datasets for validating the Phase 2B Data Inspector and Phase 2C Scanner.  
**References:** `docs/architecture.md`, `docs/data-model.md`, `archive/development/Phase 2A/archive-phase-2a-decision-log.md`

---

## 1. Overview

To validate the catalog model and verify the Data Inspector in Phase 2B, we use synthetic test fixtures rather than scanning personal photo collections. 

Each scenario defines:
- **Filesystem State:** The files, directories, and byte properties present on disk.
- **Expected Catalog State:** How the relational database entities (`Photo`, `File`, `FileVersion`, `Finding`, `ScanRun`, `ScanEvent`, `PhotoDerivation`) must represent this state.
- **Inspector Verification:** What the Data Inspector views must display to satisfy the Phase 2B validation criteria.

---

## 2. Validation Scenarios

### Scenario 1: Standard Photograph
- **Filesystem:** Single file `2024/05/img_001.jpg` (1.2 MB, valid JPEG).
- **Expected Catalog State:**
  - 1 `Photo` (status: `active`).
  - 1 `File` (rel_path: `2024/05/img_001.jpg`, state: `present`).
  - 1 `FileVersion` (linked to File, recording SHA-256, size, and mtime).
  - 1 `ScanRun` (status: `completed`).
  - `ScanEvent`: `file_discovered`, `version_created`.
- **Inspector Check:** Navigating from the Photo shows the File and its current version.

### Scenario 2: Physical Duplicate Files
- **Filesystem:** 
  - `originals/2024/img_002.jpg` (SHA-256: `hash_A`)
  - `backup/2024/img_002_copy.jpg` (SHA-256: `hash_A`)
- **Expected Catalog State:**
  - 1 `Photo` (status: `active`).
  - 2 distinct `File` records (`file_id` 1 and `file_id` 2), both referencing the same `photo_id`.
  - 2 `FileVersion` records (or shared hash reference) recording `hash_A`.
- **Inspector Check:** Inspecting the Photo displays both physical files at their respective paths. Deleting one copy leaves the Photo `active`.

### Scenario 3: RAW + JPEG Companion Representation
- **Filesystem:**
  - `2024/vacation/DSC_0100.NEF` (RAW file, 24 MB)
  - `2024/vacation/DSC_0100.JPG` (Camera-generated JPEG, 4 MB)
- **Expected Catalog State:**
  - 1 `Photo`.
  - 2 `File` records associated with the single `Photo`.
  - Each File has its own distinct `FileVersion` and SHA-256.
- **Inspector Check:** The Photo detail view lists both the RAW master and the JPEG representation as belonging to the same logical photograph.

### Scenario 4: In-Place File Modification (Metadata / Content Update)
- **Filesystem:**
  - Scan 1: `2024/img_004.jpg` has content `hash_1` (mtime $T_1$).
  - Scan 2: File is edited in-place (e.g. EXIF tag added); content becomes `hash_2` (mtime $T_2$).
- **Expected Catalog State:**
  - The `File` retains its stable `file_id`.
  - The `Photo` retains its stable `photo_id`.
  - 2 `FileVersion` records exist under the `File`: Version 1 (`hash_1`) and Version 2 (`hash_2`).
  - `ScanEvent`: `file_modified` logged under ScanRun 2.
- **Inspector Check:** File detail view shows the version history with Version 2 active and Version 1 historical.

### Scenario 5: File Move / Rename
- **Filesystem:**
  - Scan 1: `inbox/photo_temp.jpg` (SHA-256: `hash_5`).
  - Scan 2: Moved to `2024/sorted/family.jpg` (identical content `hash_5`).
- **Expected Catalog State:**
  - The original `File` record is identified by content and path history.
  - Path updated to `2024/sorted/family.jpg`.
  - `ScanEvent`: `file_moved` (from `inbox/photo_temp.jpg` to `2024/sorted/family.jpg`).
- **Inspector Check:** File detail view shows the new path along with the historical move event.

### Scenario 6: Missing / Deleted File & Missing Photo
- **Filesystem:**
  - Scan 1: `2024/img_006.jpg` exists.
  - Scan 2: File is deleted from disk.
- **Expected Catalog State:**
  - `File` state transitions to `missing`.
  - Since this was the only File for the Photo, the `Photo` status transitions to `missing`.
  - No database records are deleted.
  - `ScanEvent`: `file_missing`.
- **Inspector Check:** Dashboard counts increment "Missing Photos" and "Missing Files". Photo detail clearly explains that its backing file is no longer present.

### Scenario 7: Unassociated Finding Promoted to File
- **Filesystem:**
  - Scan 1: `documents/unknown_file.bin` discovered with an ambiguous or unsupported extension.
- **Expected Catalog State:**
  - 1 `Finding` record created (state: `current`, classification: `unsupported_format`).
  - No `Photo` or `File` record created.
  - Scan 2 (Manual/Rule Classification): Finding classified as supported image.
  - 1 new `Photo` and 1 new `File` created; Finding state updated to `classified` with `classified_file_id`.
- **Inspector Check:** Finding detail links to the newly created File, preserving the discovery provenance.

### Scenario 8: Derived Photo (Crop / Retouch)
- **Filesystem:**
  - `2024/landscape.jpg` (Original capture)
  - `2024/landscape_cropped.jpg` (Cropped version)
- **Expected Catalog State:**
  - 2 distinct `Photo` records (`Photo A` and `Photo B`).
  - 1 `PhotoDerivation` entry linking `derived_photo_id = B` to `source_photo_id = A` (derivation_type: `crop`).
- **Inspector Check:** Photo A lists Photo B under "Derivatives". Photo B lists Photo A under "Source Photos".

### Scenario 9: Multi-Parent Composite Derivation
- **Filesystem:**
  - `2024/portrait_subject.jpg` (Photo A)
  - `2024/background.jpg` (Photo B)
  - `2024/composite.jpg` (Photo C)
- **Expected Catalog State:**
  - `photo_derivation` contains two entries for `derived_photo_id = C` (`source_photo_id = A` and `source_photo_id = B`).
- **Inspector Check:** Inspecting Photo C clearly displays both parent sources in the derivation graph.

### Scenario 10: Unavailable Root / Incomplete Scan
- **Filesystem:**
  - ScanRoot `/mnt/external_disk` is unmounted or offline when a scan is triggered.
- **Expected Catalog State:**
  - `ScanRun` marked as `failed` (or `cancelled`).
  - Existing files under this root **must not** be marked missing.
  - `ScanEvent`: `root_unavailable` logged.
- **Inspector Check:** Dashboard shows the failed ScanRun; files under the root remain in `present` state.

### Scenario 11: Hash Conflict Across Conflicting Photos
- **Filesystem:**
  - Two distinct photos with distinct EXIF capture dates or metadata, but identical image payload hashes (or deliberate synthetic collision).
- **Expected Catalog State:**
  - Files are not silently merged into one Photo.
  - A conflict event is recorded, flagging the pair for human review.
- **Inspector Check:** Photos view highlights the conflict proposal rather than presenting a forced merge.

---

## 3. Implementation in Phase 2B

A test fixture generator script (`tests/fixtures/generate_catalog.py`) will programmatically construct these scenarios in a clean SQLite database. 

The Data Inspector frontend can then be exercised directly against this predictable dataset to verify all views, relationship links, and edge cases.
