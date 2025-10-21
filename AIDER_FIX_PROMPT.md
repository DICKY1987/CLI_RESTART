# Aider Prompt: Fix Remaining Linting Errors

## Context

This is the **CLI Orchestrator** project - a deterministic, schema-driven CLI orchestrator combining workflow automation, trading systems, GUI components, and AI adapters. The codebase targets **Python 3.9+** compatibility.

We've already fixed 2,394 errors using ruff auto-fixes. **349 errors remain** that require manual fixes.

## Error Report

Read `error_report.json` in the project root for the complete analysis. Key statistics:
- **40 syntax errors** (mostly f-string backslash escapes incompatible with Python 3.9-3.11)
- **77 F405 errors** (undefined names from star imports)
- **43 F401 errors** (unused imports)
- **38 B904 errors** (missing `raise ... from e`)
- **37 F821 errors** (undefined names)
- **26 E722 errors** (bare except clauses)

## Your Task

Fix ALL remaining errors in priority order. Work systematically through each category:

### Priority 1: Fix Syntax Errors (40 errors - CRITICAL)

**Problem:** F-strings with backslash escapes fail on Python 3.9-3.11 (syntax added in Python 3.12)

**Files affected (check error_report.json → critical_issues → syntax_errors):**
- `CLI_PY_GUI/gui_terminal/enhanced_pty_terminal.py`
- `scripts/registry_codegen.py`
- Others listed in the report

**Fix approach:**
```python
# BEFORE (fails Python 3.9-3.11)
f"path\\{variable}"

# AFTER - Option 1: Use raw f-string
rf"path\{variable}"

# AFTER - Option 2: Double escape
f"path\\\\{variable}"

# AFTER - Option 3: Concatenate
f"path\\" + f"{variable}"

# AFTER - Option 4: Use os.path.join or pathlib
from pathlib import Path
Path("path") / variable
```

**Action:** Find all f-strings with `\` escapes and apply one of the fixes above based on context.

### Priority 2: Replace Star Imports (77 F405 errors)

**Problem:** `from module import *` makes names undefined for linters

**Files affected:**
- `CLI_PY_GUI/gui_terminal/enhanced_pty_terminal.py` (96 errors total, mostly this)
- Check `error_report.json → critical_issues → import_issues`

**Fix approach:**
```python
# BEFORE
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

# AFTER - Replace with explicit imports
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QLineEdit,
    QMessageBox, QDialog, QTabWidget, QSplitter
)
```

**Action:**
1. For each file with F403/F405 errors, analyze what names are actually used
2. Replace `from X import *` with explicit imports
3. Run `ruff check <file>` after each file to verify all names are imported

### Priority 3: Remove Unused Imports (43 F401 errors)

**Files affected:** Check `error_report.json → critical_issues → import_issues` for F401

**Fix approach:**
```python
# BEFORE
import os
import sys
import unused_module  # F401

def main():
    print(sys.version)

# AFTER
import sys

def main():
    print(sys.version)
```

**Action:** Simply remove imports marked as F401 (unused)

### Priority 4: Add Exception Types to Bare Except (26 E722 errors)

**Files affected:** Search for `E722` in `error_report.json → errors_by_file`

**Fix approach:**
```python
# BEFORE
try:
    risky_operation()
except:  # E722 bare except
    handle_error()

# AFTER
try:
    risky_operation()
except Exception:
    handle_error()
```

**Action:** Replace `except:` with `except Exception:` (or more specific exception types if context is clear)

### Priority 5: Add Exception Chaining (38 B904 errors)

**Fix approach:**
```python
# BEFORE
try:
    operation()
except ValueError:
    raise RuntimeError("Failed")  # B904

# AFTER
try:
    operation()
except ValueError as e:
    raise RuntimeError("Failed") from e
```

**Action:** Add `from e` to raise statements inside except blocks

### Priority 6: Fix Undefined Names (37 F821 errors)

**Files affected:** Check `error_report.json → critical_issues → undefined_names`

**Common issues:**
- `TERM` not defined → add `import os; TERM = os.environ.get('TERM', 'xterm')`
- Variables used before assignment → review logic flow
- Missing imports → add appropriate imports

**Action:** Review each F821 error individually and add missing definitions/imports

### Priority 7: Other Minor Fixes

- **E702** (3 errors): Multiple statements on semicolon → split into separate lines
- **E501** (13 errors): Line too long → break into multiple lines (black should handle most)
- **E402** (31 errors): Module import not at top → move imports to top of file
- **ARG002/ARG005** (15 errors): Unused arguments → prefix with `_` if intentional
- **UP035** (2 errors): Deprecated `typing.Dict` → use `dict` instead

## Constraints

1. **Python 3.9+ compatibility required** - Do NOT use Python 3.12+ syntax
2. **Preserve functionality** - Don't change logic, only fix linting errors
3. **Follow project style:**
   - Line length: 88 characters (black default)
   - Use `from typing import Dict, Optional` for type hints (not `dict | None` syntax)
4. **Don't fix files in `archive/` directory** - They're deprecated
5. **Test after fixes:** Run `ruff check .` to verify no new errors introduced

## Systematic Approach

**Work through files in order of error count (from error_report.json → top_files):**

1. `CLI_PY_GUI/gui_terminal/enhanced_pty_terminal.py` (96 errors)
2. `scripts/registry_codegen.py` (32 errors)
3. `src/cli_multi_rapid/main.py` (29 errors)
4. Continue through remaining files...

**For each file:**
1. Read the error list from `error_report.json → errors_by_file → <filename>`
2. Fix all errors in priority order (syntax → imports → exceptions → style)
3. Verify with `ruff check <filename>`
4. Move to next file

## Verification

After all fixes, verify:
```bash
# Should show 0 errors (or close to it)
ruff check .

# Should compile successfully
python -m compileall src/ CLI_PY_GUI/

# Run tests if available
pytest tests/ -v
```

## Expected Outcome

- **0 syntax errors** (all 40 fixed)
- **0 import errors** (F403, F405, F401 fixed)
- **Significant reduction** in other error categories
- **All Python files compile** successfully
- **Project passes linting** for CI/CD

## Start Here

Begin with Priority 1 (syntax errors) and work through systematically. Use the error_report.json file as your reference for line numbers and specific errors. Ask if you need clarification on any specific error type.

**Ready? Start with the syntax errors in `CLI_PY_GUI/gui_terminal/enhanced_pty_terminal.py` first.**
