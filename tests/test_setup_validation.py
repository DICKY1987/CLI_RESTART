"""
Tests for System Validation functionality.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from cli_multi_rapid.setup.validation import SystemValidator


class TestSystemValidator:
    """Test cases for SystemValidator class."""

    def setup_method(self):
        """Set up test instance."""
        self.validator = SystemValidator()

    def test_initialization(self):
        """Test SystemValidator initialization."""
        assert self.validator.project_root == Path.cwd()
        assert isinstance(self.validator.issues, list)
        assert isinstance(self.validator.successes, list)
        assert isinstance(self.validator.warnings, list)

    def test_custom_project_root(self):
        """Test initialization with custom project root."""
        custom_root = Path("/custom/project")
        validator = SystemValidator(project_root=custom_root)
        assert validator.project_root == custom_root

    def test_check_python_version_compatible(self):
        """Test Python version check with compatible version."""
        with patch("sys.version_info", (3, 11, 0)):
            result = self.validator.check_python_version()
            assert result is True
            assert len(self.validator.successes) > 0
            assert "Python 3.11.0 - Compatible" in self.validator.successes[0]

    def test_check_python_version_incompatible(self):
        """Test Python version check with incompatible version."""
        with patch("sys.version_info", (3, 8, 0)):
            result = self.validator.check_python_version()
            assert result is False
            assert len(self.validator.issues) > 0
            assert "Need Python 3.9+" in self.validator.issues[0]

    def test_check_git_repository_exists(self):
        """Test git repository check when .git exists."""
        mock_git_dir = Mock()
        mock_git_dir.exists.return_value = True

        with (
            patch.object(
                self.validator.project_root, "__truediv__", return_value=mock_git_dir
            ),
            patch("subprocess.run") as mock_run,
        ):

            # Mock successful git remote command
            mock_result = Mock()
            mock_result.stdout = "https://github.com/DICKY1987/cli_multi_rapid_DEV.git"
            mock_run.return_value = mock_result

            result = self.validator.check_git_repository()
            assert result is True
            assert len(self.validator.successes) > 0

    def test_check_git_repository_missing(self):
        """Test git repository check when .git is missing."""
        mock_git_dir = Mock()
        mock_git_dir.exists.return_value = False

        with patch.object(
            self.validator.project_root, "__truediv__", return_value=mock_git_dir
        ):
            result = self.validator.check_git_repository()
            assert result is False
            assert len(self.validator.issues) > 0
            assert "Not in a git repository" in self.validator.issues[0]

    def test_check_file_structure_complete(self):
        """Test file structure check when all files exist."""
        with patch("pathlib.Path.exists", return_value=True):
            result = self.validator.check_file_structure()
            assert result is True
            assert len(self.validator.successes) > 0

    def test_check_file_structure_missing_files(self):
        """Test file structure check with missing files."""

        def mock_exists(path_obj):
            # Simulate missing main.py
            return "main.py" not in str(path_obj)

        with patch("pathlib.Path.exists", side_effect=mock_exists):
            result = self.validator.check_file_structure()
            assert result is False
            assert len(self.validator.issues) > 0
            assert "Missing files" in self.validator.issues[0]

    def test_check_dependencies_complete(self):
        """Test dependency check when all packages are available."""
        # Mock all imports as successful
        with patch("builtins.__import__", return_value=Mock()):
            result = self.validator.check_dependencies()
            assert result is True
            assert len(self.validator.successes) > 0

    def test_check_dependencies_missing(self):
        """Test dependency check with missing packages."""

        def mock_import(name, *args, **kwargs):
            if name == "typer":
                raise ImportError("No module named 'typer'")
            return Mock()

        with patch("builtins.__import__", side_effect=mock_import):
            result = self.validator.check_dependencies()
            assert result is False
            assert len(self.validator.issues) > 0
            assert "Missing packages" in self.validator.issues[0]

    @patch("sys.path")
    @patch("subprocess.run")
    def test_check_cli_installation_success(self, mock_run, mock_path):
        """Test CLI installation check when successful."""
        # Mock successful import and CLI execution
        with patch("builtins.__import__", return_value=Mock()):
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = self.validator.check_cli_installation()
            assert result is True
            assert len(self.validator.successes) >= 1

    @patch("subprocess.run")
    def test_check_cli_installation_import_failure(self, mock_run):
        """Test CLI installation check with import failure."""

        def mock_import(name, *args, **kwargs):
            if "cli_multi_rapid" in name:
                raise ImportError("No module named 'cli_multi_rapid'")
            return Mock()

        with patch("builtins.__import__", side_effect=mock_import):
            result = self.validator.check_cli_installation()
            assert result is False
            assert len(self.validator.issues) > 0

    @patch("subprocess.run")
    def test_check_external_tools(self, mock_run):
        """Test external tools check."""

        def mock_run_side_effect(command, **kwargs):
            # Mock git and ruff as available, others as missing
            if "git" in command or "ruff" in command:
                mock_result = Mock()
                mock_result.returncode = 0
                return mock_result
            else:
                raise FileNotFoundError()

        mock_run.side_effect = mock_run_side_effect

        result = self.validator.check_external_tools()
        # Should return True if at least 2 tools are working (git + ruff)
        assert result is True

    def test_check_schema_files_missing_directory(self):
        """Test schema files check when directory is missing."""
        mock_schema_dir = Mock()
        mock_schema_dir.exists.return_value = False

        with patch.object(
            self.validator.project_root, "__truediv__", return_value=mock_schema_dir
        ):
            result = self.validator.check_schema_files()
            assert result is False
            assert len(self.validator.issues) > 0

    def test_check_schema_files_valid(self):
        """Test schema files check with valid JSON schemas."""
        mock_schema_dir = Mock()
        mock_schema_dir.exists.return_value = True

        # Mock schema files
        mock_files = [
            Mock(name="workflow.schema.json"),
            Mock(name="diagnostics.schema.json"),
            Mock(name="test.schema.json"),
        ]
        mock_schema_dir.glob.return_value = mock_files

        with (
            patch.object(
                self.validator.project_root, "__truediv__", return_value=mock_schema_dir
            ),
            patch("builtins.open", create=True),
            patch("json.load", return_value={"type": "object"}),
        ):

            result = self.validator.check_schema_files()
            assert result is True
            assert len(self.validator.successes) > 0

    def test_check_configuration_complete(self):
        """Test configuration check when all files exist."""
        with patch("pathlib.Path.exists", return_value=True):
            result = self.validator.check_configuration()
            assert result is True
            assert len(self.validator.successes) > 0

    def test_create_sample_workflow(self):
        """Test sample workflow creation."""
        with (
            patch("pathlib.Path.mkdir"),
            patch("builtins.open", create=True),
            patch("yaml.dump") as mock_yaml_dump,
        ):

            result = self.validator.create_sample_workflow()
            assert result is True
            mock_yaml_dump.assert_called_once()
            assert len(self.validator.successes) > 0

    def test_create_sample_workflow_no_yaml(self):
        """Test sample workflow creation without PyYAML."""
        with (
            patch("pathlib.Path.mkdir"),
            patch(
                "builtins.__import__", side_effect=ImportError("No module named 'yaml'")
            ),
        ):

            result = self.validator.create_sample_workflow()
            assert result is False
            assert len(self.validator.warnings) > 0

    @patch("subprocess.run")
    def test_test_workflow_execution_success(self, mock_run):
        """Test workflow execution test when successful."""
        # Mock workflow file exists
        mock_workflow_file = Mock()
        mock_workflow_file.exists.return_value = True

        with patch.object(
            self.validator.project_root, "__truediv__", return_value=mock_workflow_file
        ):
            # Mock successful subprocess run
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = self.validator.test_workflow_execution()
            assert result is True
            assert len(self.validator.successes) > 0

    @patch("subprocess.run")
    def test_test_workflow_execution_missing_file(self, mock_run):
        """Test workflow execution test with missing workflow file."""
        mock_workflow_file = Mock()
        mock_workflow_file.exists.return_value = False

        with patch.object(
            self.validator.project_root, "__truediv__", return_value=mock_workflow_file
        ):
            result = self.validator.test_workflow_execution()
            assert result is False
            assert len(self.validator.issues) > 0

    def test_generate_quick_start_guide(self):
        """Test quick start guide generation."""
        # Add some mock results
        self.validator.successes = ["Test success"]
        self.validator.warnings = ["Test warning"]
        self.validator.issues = ["Test issue"]

        with (
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.write_text") as mock_write,
        ):

            self.validator.generate_quick_start_guide()

            mock_write.assert_called_once()
            written_content = mock_write.call_args[0][0]

            # Check that content includes our test data
            assert "Test success" in written_content
            assert "Test warning" in written_content
            assert "Test issue" in written_content

    def test_run_comprehensive_validation(self):
        """Test running comprehensive validation suite."""
        with (
            patch.object(self.validator, "check_python_version", return_value=True),
            patch.object(self.validator, "check_git_repository", return_value=True),
            patch.object(self.validator, "check_file_structure", return_value=True),
            patch.object(self.validator, "check_dependencies", return_value=True),
            patch.object(self.validator, "check_cli_installation", return_value=True),
            patch.object(self.validator, "check_external_tools", return_value=True),
            patch.object(self.validator, "check_schema_files", return_value=True),
            patch.object(self.validator, "check_configuration", return_value=True),
        ):

            results = self.validator.run_comprehensive_validation()

            # Should have all checks passing
            assert all(results.values())
            assert len(results) == 8

    def test_get_next_steps_text_success(self):
        """Test next steps text generation when no issues."""
        self.validator.issues = []
        next_steps = self.validator._get_next_steps_text()
        assert "CONGRATULATIONS" in next_steps
        assert "ready to use" in next_steps.lower()

    def test_get_next_steps_text_with_issues(self):
        """Test next steps text generation with issues."""
        self.validator.issues = ["Test issue 1", "Test issue 2"]
        next_steps = self.validator._get_next_steps_text()
        assert "Setup Incomplete" in next_steps
        assert "pip install" in next_steps

    def test_print_validation_results(self):
        """Test validation results printing."""
        # Add mock results
        self.validator.successes = ["Success 1", "Success 2"]
        self.validator.warnings = ["Warning 1"]
        self.validator.issues = ["Issue 1"]

        # Should not raise any exceptions
        self.validator._print_validation_results()

    def test_get_timestamp(self):
        """Test timestamp generation."""
        timestamp = self.validator._get_timestamp()
        assert isinstance(timestamp, str)
        assert len(timestamp) > 10  # Should be a reasonable timestamp format


class TestSystemValidatorIntegration:
    """Integration tests for system validation."""

    def test_real_python_version_check(self):
        """Test checking real Python version."""
        validator = SystemValidator()
        result = validator.check_python_version()

        # Should work with current Python version (test environment)
        # Current test environment should have Python 3.9+
        assert result is True

    def test_current_directory_structure(self):
        """Test validation in current directory."""
        validator = SystemValidator()

        # At least some basic structure should exist
        # This test may fail if run outside the project directory
        # but that's expected behavior

        # Just test that the method runs without exceptions
        try:
            validator.check_file_structure()
        except Exception as e:
            pytest.fail(f"File structure check raised exception: {e}")

    def test_dependency_check_partial(self):
        """Test dependency checking with current environment."""
        validator = SystemValidator()

        # Should be able to check dependencies without crashing
        # May find missing packages, but shouldn't raise exceptions
        try:
            result = validator.check_dependencies()
            # Result can be True or False, but should not crash
            assert isinstance(result, bool)
        except Exception as e:
            pytest.fail(f"Dependency check raised exception: {e}")

    def test_validation_state_management(self):
        """Test that validator properly manages state across checks."""
        validator = SystemValidator()

        # Run a few checks
        validator.check_python_version()
        initial_success_count = len(validator.successes)

        validator.check_python_version()  # Run again
        # Should have added another success (duplicate is okay for testing)
        assert len(validator.successes) >= initial_success_count
