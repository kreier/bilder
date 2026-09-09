# Security Policy

## Scope

Bilder is intended to manage a private personal photo archive.

The system may eventually process highly sensitive information contained in photographs and their metadata, including:

- filenames
- timestamps
- GPS coordinates
- camera information
- personal photographs
- cloud-service identifiers
- filesystem paths

Security and privacy are therefore core design requirements.

## Supported versions

Bilder is currently in early development.

There are no stable production releases of the new system yet.

The previous implementation is preserved under `archive/` and is not considered the active system.

## Reporting a vulnerability

If you discover a security vulnerability in Bilder, please do not publish the details immediately in a public GitHub issue.

Instead, report the issue privately through the security reporting mechanism provided by GitHub for this repository, when available.

If private reporting is not yet configured, contact the project maintainer privately before disclosing sensitive details.

## Secrets

Never commit secrets to the repository.

This includes:

- passwords
- API keys
- OAuth tokens
- cloud credentials
- private keys
- session cookies
- authentication tokens
- private network credentials

Use environment variables or another appropriate secret-management mechanism.

Example configuration files must contain placeholders only.

## Personal data

Real photographs and personal metadata must never be committed to the public repository.

This includes:

- original photographs
- thumbnails containing personal photographs
- GPS coordinates
- private filenames
- personal filesystem paths
- iCloud identifiers
- Google Drive identifiers
- private database files
- database exports containing personal records

Development should use synthetic or sanitized test data.

## Database

The production photo database is private and must not be stored in the public repository.

Only schema definitions, migrations, documentation, and synthetic test databases may be committed.

## Public statistics

Aggregate statistics may be published when intentionally designed for public release.

Statistics must be reviewed to ensure that they do not expose individual photographs, private filenames, precise locations, cloud identifiers, or other personal information.

## Incident response

If a secret or private data is accidentally committed:

1. Stop using the exposed credential or data.
2. Revoke or rotate credentials where applicable.
3. Remove the sensitive content from the repository.
4. Assess whether repository history also needs to be rewritten.
5. Document the incident and corrective action.

Removing a secret from the latest commit is not sufficient if the secret remains accessible in Git history.

## Security principles

Bilder should favor:

- least privilege
- explicit authorization
- local ownership of data
- encrypted transport
- authenticated APIs
- reversible operations
- audit trails
- safe defaults
- minimal exposure of personal metadata