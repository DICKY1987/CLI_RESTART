This PR introduces a test harness for a safe no-launch mode and associated Pester tests.

Summary
- Add -NoLaunch mode to restart.ps1 to avoid spawning panes during tests.
- Generate session artifacts under .sessions/{id}:
  - manifest.json
  - preflight.md
- Add Pester tests (v3-compatible):
  - tests/pester/Launcher.Unit.Tests.ps1
  - tests/pester/Launcher.Integration.Tests.ps1
  - tests/pester/Config.Validation.Tests.ps1
- Ignore .sessions/ and .tmp-tests/ in .gitignore.

Acceptance Criteria
- Invoke-Pester passes locally with:
  powershell -NoProfile -Command Invoke-Pester -Path "CLI_RESTART/tests/pester" -EnableExit
- No panes/processes are launched during tests.

How to run locally
- powershell -NoProfile -Command Invoke-Pester -Path "CLI_RESTART/tests/pester/Launcher.*.Tests.ps1" -EnableExit
- powershell -NoProfile -Command Invoke-Pester -Path "CLI_RESTART/tests/pester" -EnableExit

Notes
- Tests use a child PowerShell process to validate error surfacing and exit-codes reliably on Windows.
- Scope of changes is limited to restart.ps1, tests, and .gitignore to minimize conflicts.
