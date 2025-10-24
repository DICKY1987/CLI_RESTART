# GUI Functionality Evaluation

date: 2025-10-23

environment: ubuntu container (python 3.11)

## Setup
- Installed Python dependencies with `pip install PyQt6 psutil` (already satisfied).

## Test Procedure
1. Attempted to launch GUI (`python -m gui_terminal.main`).
2. Planned to run GUI tests (`pytest tests/gui -q`).

## Results
- Server startup failed immediately with `ImportError: libEGL.so.1: cannot open shared object file` when PyQt6 attempted to import Qt GUI modules.
- Subsequent attempt with `QT_QPA_PLATFORM=minimal` produced the same missing `libEGL` error.
- Without the server running, the parity harness could not connect and reported `[Errno 111] Connection refused` for every scenario.
- Attempts to install `libEGL` through `apt-get update` were blocked by repository access restrictions (HTTP 403), preventing remediation inside this environment.

## Conclusion
The GUI could not be functionally evaluated because the PyQt6 runtime depends on `libEGL.so.1`, which is unavailable and cannot be installed due to restricted package repositories. All automated parity tests therefore failed at connection setup. Further evaluation requires installing the missing system library (e.g., `apt-get install -y libegl1`).
