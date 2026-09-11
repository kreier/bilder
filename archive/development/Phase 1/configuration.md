# Bilder — Configuration

## Status

This document defines the configuration model for Bilder.

It describes deployment settings, source configuration, test environments, and credential handling. Actual private configuration values and credentials must not be committed to the repository.

## Configuration Principles

Bilder separates three kinds of information:

1. **Catalogue data** — stored in the Bilder database and describing photos, files, sources, observations, and history.
2. **Runtime configuration** — describing how a particular Bilder installation connects to storage and services.
3. **Secrets** — credentials and private keys required to access protected resources.

Configuration may change without changing the identity of a `Source` in the catalogue.

## Runtime Configuration

Runtime configuration may include:

- database location
- Bilder server bind address and port
- NAS address and share/path
- local filesystem paths
- thumbnail/cache locations
- log locations
- worker settings
- scan defaults
- external service endpoints
- container-specific paths

A committed example configuration should document the available settings without containing private values.

Recommended location:

```text
config/
├── config.example.toml
└── config.toml
```

`config.example.toml` may be committed.

`config.toml` should normally be excluded from Git.

## Sources

A configured connection to a storage system is not necessarily the same thing as a catalogue Source.

For example:

```text
Configuration
    NAS address: 192.168.x.x
    NAS share:   /photos

Catalogue
    Source: Main NAS
```

The network address or mount path may change while the historical `Source` remains the same.

A Source should therefore have a persistent identity independent of its current access path where possible.

Examples of Sources include:

- main NAS
- old HDD
- removable disk
- SD card
- local filesystem
- cloud storage
- other external archive

## NAS Configuration

The NAS configuration should eventually describe:

- network address or hostname
- protocol
- share
- mount/access path
- read/write capability
- connection method
- optional source-specific settings

The NAS is intended to be the canonical archive storage.

Bilder must not assume that a network path itself is the identity of the NAS Source.

## Other Hosts and Services

If Bilder is deployed across several machines, configuration may contain endpoints for services such as:

- Bilder server
- database
- NAS
- thumbnail storage
- background workers
- future macOS bridge
- future AI/analysis services

For development and testing, these should be configurable rather than hard-coded.

## Credentials and Secrets

Credentials must never be committed to the repository.

Examples include:

- NAS usernames and passwords
- API tokens
- private keys
- encryption keys
- service credentials
- TLS private keys

Possible mechanisms include:

- environment variables
- Docker secrets
- protected secret files
- operating-system credential stores

The repository should document **which credential is required and how it is supplied**, but never contain the actual secret.

## Example Configuration

A future `config.example.toml` may look conceptually like:

```text
[database]
path = "/data/bilder/bilder.db"

[server]
host = "0.0.0.0"
port = 8080

[nas]
address = "nas.example.local"
share = "/photos"
mount_path = "/mnt/nas/photos"

[storage]
thumbnail_path = "/data/bilder/thumbnails"
log_path = "/data/bilder/logs"
```

This is only an example. Actual deployment values should be kept outside the repository.

## Development Environments

Bilder should support separate configurations for:

- local development
- WSL2 development
- Docker development
- Raspberry Pi deployment
- future production deployment

A development environment must never accidentally point a destructive operation at the real photo archive.

During early development, operations should preferably be restricted to test datasets.

## Test Configuration

Each development phase should use a defined test configuration containing at least:

- dataset identity
- database path
- source path
- Bilder version
- database schema version
- scan mode
- relevant feature flags

Each phase should normally start with a fresh database.

Previous databases may be retained as test artifacts for comparison and regression analysis.

## Reproducibility

A test result should be reproducible from:

```text
Dataset
+
Bilder version
+
Database schema version
+
Configuration
+
Operation
```

Where practical, the test runner should record these values with the test result.

## Configuration vs. Database

Configuration answers:

> How does this Bilder installation access its environment?

The database answers:

> What does Bilder know about the archive and its history?

For example:

```text
Configuration:
    NAS address = current-nas.example

Database:
    Source = Main NAS
    SourceCopy = /Photos/2026/08-23_Concert/IMG_1234.JPG
```

Changing the NAS address should not rewrite the historical identity of the Source.

## Security

The following rules apply:

- Never commit credentials or private keys.
- Never put real passwords in example configuration files.
- Keep production configuration separate from test configuration.
- Do not point destructive development operations at the real archive.
- Prefer read-only access during scanning and catalogue development.
- Treat generated logs as potentially sensitive because paths and metadata may reveal personal information.
- Do not expose NAS credentials or other secrets through the web UI.

## Future Configuration Areas

Configuration may later include:

- metadata extraction settings
- thumbnail generation settings
- face-analysis settings
- pHash/pixel-hash settings
- preservation policies
- quarantine location
- backup targets
- external metadata services
- AI/LLM endpoints
- authentication settings
- retention policies

These should be introduced only when the corresponding feature is implemented.

## Initial Configuration Checklist

Before the first real NAS scan, the deployment should define:

[ ] database location
[ ] Bilder server address/port
[ ] NAS address/hostname
[ ] NAS share/path
[ ] NAS access method
[ ] credentials mechanism
[ ] test dataset location
[ ] log location
[ ] thumbnail/cache location
[ ] read-only or read/write access mode

## Guiding Principle

Configuration describes the environment in which Bilder operates.

The database describes the archive.

Secrets provide access to protected resources.

These concerns should remain separate.
