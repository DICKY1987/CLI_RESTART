Disaster Recovery Plan

Objectives
- RTO: <= 2 hours for registry database.
- RPO: <= 15 minutes (based on backup cadence and WAL/archive policy for Postgres; N/A for SQLite).

Procedures
- Declare incident, assign incident lead, notify stakeholders.
- Retrieve latest valid backup from local `.backups/` or remote storage.
- Provision replacement database (SQLite file or Postgres instance).
- Run restore procedure and smoke validation.
- Re-point orchestrator `DATABASE_URL` and resume operations.

Escalation & Contacts
- Primary: Core maintainers
- Secondary: Platform/Infra on-call

Drills
- Run a quarterly tabletop and one full restore exercise.

