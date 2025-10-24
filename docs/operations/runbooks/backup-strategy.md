Backup and Restore Strategy

- Scope: registry database (SQLite by default; Postgres supported via external tools).
- Backup cadence: on-demand with retention policy guidance below.

Implementation
- Scripts: `scripts/backup_database.sh|.ps1` and `scripts/restore_database.sh|.ps1`.
- Environment: `DATABASE_URL`. Defaults to `sqlite:///.data/registry.db`.
- SQLite: Python-based file copy (consistent when DB is not in use).
- Postgres: use `pg_dump`/`pg_restore` (not bundled); integrate in CI/CD as needed.

Retention Policy
- Local: keep last 30 daily backups in `.backups/`.
- Remote: optionally upload backups to S3/Azure Blob for 90 days.

Validation
- Periodic restore tests into a scratch database, verifying core tables and recent records are present.

