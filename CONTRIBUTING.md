# Contributing to Bilder

Bilder is currently in early development and is primarily being developed as a personal self-hosted photo management system.

The project is being built incrementally, with an emphasis on careful architecture and data safety.

## Before contributing

Please read:

- [`README.md`](README.md)
- [`AGENTS.md`](AGENTS.md)
- [`SECURITY.md`](SECURITY.md)
- the relevant documentation under [`docs/`](docs/)

The architecture is still evolving. A proposed implementation may therefore be rejected if it conflicts with the documented direction of the project.

## Development principles

Contributions should favor:

- small changes
- simple implementations
- clear documentation
- testability
- privacy
- data safety
- reversible operations

Avoid introducing unnecessary dependencies or infrastructure.

## Photo data

Never use real personal photographs or personal metadata in commits, pull requests, tests, screenshots, or examples.

Use synthetic or sanitized data instead.

Never submit:

- real filenames
- private filesystem paths
- GPS coordinates
- iCloud identifiers
- Google Drive identifiers
- real database contents
- authentication credentials

## Changes to the architecture

Significant architectural changes should be discussed before implementation.

If a decision has long-term architectural consequences, document it as an Architecture Decision Record under:

```text
docs/decisions/
```

## Code changes

Keep commits focused on one logical change.

Include tests when practical.

Do not mix unrelated refactoring with feature work unless there is a clear reason.

## Testing

Tests must not require access to the real photo archive, NAS, Apple account, Google account, or other personal services.

Use fixtures, temporary directories, mock data, and test databases.

## Destructive operations

Any functionality that can modify or delete photographs requires particular care.

New destructive functionality should:

- be explicitly identified
- support a dry-run or preview where practical
- record the intended operation
- require explicit approval
- provide a verification step
- avoid irreversible deletion by default

## Pull requests

Pull requests should explain:

- what was changed
- why it was changed
- how it was tested
- whether documentation was updated
- whether the change affects the data model or architecture

Keep pull requests small enough to review comfortably.

## Generated files

Do not commit generated files unless they are intentionally part of the project.

In particular, do not commit:

- production databases
- private photo data
- generated thumbnails from the personal archive
- private exports
- local configuration files

## Historical code

The `archive/` directory contains the previous implementation.

Changes to archived code should normally be avoided unless the task specifically concerns historical maintenance.

New functionality belongs in the new system rather than being added to the archived implementation.