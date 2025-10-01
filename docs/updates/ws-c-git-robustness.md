Title: Git Robustness & Offline Enforcement
Branch: ws/c-git-robustness
Summary: Track branch creation for the Git robustness workstream and enable PR creation with a minimal, non-functional documentation change.

Scope
- Capture non-FF pull errors to error.txt and halt
- Ensure offline mode bypasses network git
- Preserve robust default-branch detection

Acceptance Criteria
- Deterministic stop on non-fast-forward
- Clean offline path without fetch/pull

Notes
- This file exists to provide a minimal diff so a PR can be opened for the workstream.
