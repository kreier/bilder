# Changelog

All notable changes to Bilder are documented here.

Bilder is in active early development. The changelog records development milestones, architectural freezes, and releases.

## Unreleased (Phase 2B — Data Inspector)

### In-Browser SQLite WASM & Web Interface
- Added in-browser SQLite WebAssembly (`sql.js`) engine in [`frontend/src/api/wasm.ts`](frontend/src/api/wasm.ts) enabling full catalog inspection directly in the browser without a live Python server.
- Bundled `sql.js` WASM binary via Vite's native asset pipeline (`?url` import) with explicit pre-fetching and in-memory instantiation.
- Updated [`frontend/src/api/client.ts`](frontend/src/api/client.ts) to provide a transparent hybrid client: queries native FastAPI on `localhost:8000` when running locally, and automatically falls back to in-browser SQLite WASM when hosted on GitHub Pages or when the backend is unreachable.
- Configured Vite base path in [`frontend/vite.config.ts`](frontend/vite.config.ts) for production builds served at `https://kreier.github.io/bilder/`.

### Deployment & CI/CD
- Added automated GitHub Actions workflow [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) to build the frontend and deploy to GitHub Pages on pushes to `0.2.0` and `main`.
- Updated GitHub Actions workflow to use Node.js 22 LTS and `actions/configure-pages@v5`.

### Architecture & Documentation
- Documented the Phase 2B Data Inspector specification in [`docs/phase-2b-inspector.md`](docs/phase-2b-inspector.md), detailing scope, views, relationship navigation, and validation criteria.
- Established the Architecture Decision Record (ADR) system and adopted [ADR 0001: Phase 2 Relational SQLite Schema](docs/decisions/0001-phase-2-schema.md) defining the concrete DDL schema for `photo`, `file`, `file_version`, `photo_derivation`, `scan_root`, `scan_run`, `scan_event`, and `finding`.
- Created [`docs/test-scenarios.md`](docs/test-scenarios.md) specifying 11 synthetic catalog scenarios (RAW+JPEG pairing, duplicate files, moves/renames, version updates, missing roots) for fixture generation and validation.
- Updated [`README.md`](README.md) to reflect the Phase 2B milestone, current directory structure, and the $\text{Photo} \to \text{File} \to \text{FileVersion}$ identity model.

---

## Phase 2A — Architecture & Data Model Freeze (2026-09-11)

- **Architecture Freeze:** Formally froze core architectural principles and non-destructive invariants in [`docs/architecture.md`](docs/architecture.md).
- **Data Model Freeze:** Formally froze the conceptual data model in [`docs/data-model.md`](docs/data-model.md), strictly separating logical Photo identity from physical File paths and SHA-256 FileVersions.
- **Configuration Contract:** Documented configuration reproducibility invariants in [`docs/configuration.md`](docs/configuration.md).
- **Design Log Archive:** Archived the 178-question architectural decision matrix and abbreviated discussions under [`archive/development/Phase 2A/`](archive/development/Phase%202A/).

---

## v0.1 — Foundation & Working Prototype (2026-09-11)

### Added
- **SQLite Database Layer:** Initial database implementation in [`src/bilder/database.py`](src/bilder/database.py) with tables for `source`, `scan_session`, `file_version`, `source_copy`, and `file_observation`.
- **Filesystem Scanner Groundwork:** Read-only scanner foundation in [`src/bilder/scanner.py`](src/bilder/scanner.py) for observing filesystem trees without mutation.
- **FastAPI Backend:** Web API in [`src/bilder/api/app.py`](src/bilder/api/app.py) providing `/api/health` and `/api/overview` endpoints.
- **Web Frontend:** Initial React 19, TypeScript, and Vite dashboard in [`frontend/`](frontend/) with summary statistics and responsive layout.
- **Project Configuration:** Established Python project packaging and test configuration in `pyproject.toml`.

---

## v26.02 — Historical System

### Previous System
- Last release of the legacy Bilder implementation containing folder-summary and collection-statistics scripts.
- Preserved under [`archive/`](archive/) for historical reference.

---

## Versioning

Bilder uses milestone and semantic versioning (`v0.1`, `0.2.0`) for active development phases, while preserving historical calendar-based tags (`v26.02`):
- **Stage 1 (Foundation):** Tagged as `v0.1`.
- **Stage 2 (Deterministic Catalog):** In active development on branch `0.2.0`.