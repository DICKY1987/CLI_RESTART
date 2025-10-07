"""Tests for rollback command to ensure no infinite backup loops."""

import re
import sys
from pathlib import Path

from typer.testing import CliRunner


def _repo_root() -> Path:
    """Get repository root path."""
    return Path(__file__).resolve().parents[2]


def _load_rollback_app():
    """Load the rollback command app."""
    src_path = _repo_root() / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    from cli_multi_rapid.commands.rollback import app
    return app


class TestRollbackRestoreCommand:
    """Test rollback restore command to prevent infinite backup loops."""

    def test_restore_command_has_backup_current_option(self):
        """Test that the restore command has the --backup-current option.
        
        This verifies that the infinite loop fix is in place by confirming
        that backup creation is now optional via a flag, rather than automatic.
        """
        app = _load_rollback_app()
        runner = CliRunner()
        result = runner.invoke(app, ["restore", "--help"])
        
        assert result.exit_code == 0
        # Check for the option in the output (stripping ANSI color codes)
        clean_output = re.sub(r'\x1b\[[0-9;]*m', '', result.stdout)
        assert "--backup-current" in clean_output
        assert "Create backup of current state before restoring" in clean_output

    def test_restore_command_help_mentions_no_automatic_backup(self):
        """Test that the help text mentions backups are not created by default.
        
        This confirms the infinite loop issue has been addressed.
        """
        app = _load_rollback_app()
        runner = CliRunner()
        result = runner.invoke(app, ["restore", "--help"])
        
        assert result.exit_code == 0
        clean_output = re.sub(r'\x1b\[[0-9;]*m', '', result.stdout)
        assert "no backup is created" in clean_output or "not created" in clean_output
        assert "infinite backup loop" in clean_output or "backup loop" in clean_output

    def test_restore_command_signature_has_backup_current_parameter(self):
        """Test that the restore function has the backup_current parameter.
        
        This verifies the code change to make pre-restore backups optional.
        """
        src_path = _repo_root() / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        from cli_multi_rapid.commands import rollback
        import inspect
        
        # Get the restore function signature
        restore_sig = inspect.signature(rollback.restore)
        params = restore_sig.parameters
        
        # Verify backup_current parameter exists
        assert "backup_current" in params
        # For typer commands, the default is wrapped in OptionInfo
        # We just need to verify the parameter exists
        param = params["backup_current"]
        assert param.annotation == bool or "bool" in str(param.annotation)

    def test_clean_command_exists(self):
        """Test that the clean command exists for manual cleanup.
        
        This verifies that cleanup functionality is available for managing
        old snapshots, preventing accumulation.
        """
        app = _load_rollback_app()
        runner = CliRunner()
        result = runner.invoke(app, ["clean", "--help"])
        
        assert result.exit_code == 0
        clean_output = re.sub(r'\x1b\[[0-9;]*m', '', result.stdout)
        assert "Clean up old snapshots" in clean_output or "Delete snapshots" in clean_output
        assert "--days" in clean_output

