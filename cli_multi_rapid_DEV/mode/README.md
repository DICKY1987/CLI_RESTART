# Codex Modification Files

This folder contains all the files needed for Codex to execute the CLI Orchestrator codebase modifications based on the simplified 25-operations framework.

## Files Included

### Core Specification
- **`codebase_modification_spec.json`** - Complete modification specification with 37 operations across 5 phases

### Execution Scripts
- **`execute_modifications.py`** - Python script for executing modifications with backup and validation
- **`execute_modifications.sh`** - Bash script for direct file operations and template creation

## Usage for Codex

### Option 1: Use the JSON Specification
Codex can parse `codebase_modification_spec.json` and execute the operations programmatically:

```python
import json

# Load the specification
with open('codebase_modification_spec.json', 'r') as f:
    spec = json.load(f)

# Execute operations in order
operations = spec['modification_specification']['operations']
```

### Option 2: Run the Python Executor
```bash
cd /path/to/target/repository
python /path/to/mode/execute_modifications.py --spec /path/to/mode/codebase_modification_spec.json
```

### Option 3: Run the Bash Script
```bash
cd /path/to/target/repository
bash /path/to/mode/execute_modifications.sh --spec /path/to/mode/codebase_modification_spec.json
```

## Modification Summary

The specification defines transformations to align the codebase with the simplified 25-operations framework:

### Deletions (9 files)
- 6 obsolete CLI workflows that exceed complexity limits
- 3 obsolete GitHub Actions workflows superseded by claude-orchestrator.yml

### Modifications (3 files)
- Align existing workflows with cost controls and simplified operations
- Add role-based assignments and complexity limits

### Creations (3 files)
- New simplified workflow templates
- Role configuration files
- Cost control schemas

### Cost & Complexity Targets
- **Per Change**: <$3.00
- **Daily Budget**: <$15.00
- **Monthly Budget**: <$300.00
- **Max Operations**: 25 per workflow
- **Max Phases**: 3 per workflow

## Safety Features

- **Backup Creation**: All files backed up before modification
- **Dry Run Mode**: Test without making changes
- **Rollback Capability**: Restore from backup if needed
- **Validation Gates**: Schema and cost validation after changes

## Framework Compliance

All modifications ensure 100% compliance with the simplified 25-operations framework discovered in branch `feature/simplified-25ops-workflows`.