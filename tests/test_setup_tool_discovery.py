"""
Tests for CLI Tool Discovery functionality.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from cli_multi_rapid.setup.tool_discovery import CLIToolDiscovery


class TestCLIToolDiscovery:
    """Test cases for CLIToolDiscovery class."""

    def setup_method(self):
        """Set up test instance."""
        self.discovery = CLIToolDiscovery()

    def test_initialization(self):
        """Test CLIToolDiscovery initialization."""
        assert self.discovery.home_dir == Path.home()
        assert isinstance(self.discovery.tool_categories, dict)
        assert "AI Tools" in self.discovery.tool_categories
        assert "Development" in self.discovery.tool_categories
        assert len(self.discovery.search_directories) > 0

    def test_custom_home_directory(self):
        """Test initialization with custom home directory."""
        custom_home = Path("/custom/home")
        discovery = CLIToolDiscovery(home_dir=custom_home)
        assert discovery.home_dir == custom_home

    def test_get_search_directories_windows(self):
        """Test search directories on Windows."""
        with patch("sys.platform", "win32"):
            discovery = CLIToolDiscovery()
            dirs = discovery._get_search_directories()

            # Check for Windows-specific directories
            windows_dirs = [d for d in dirs if "AppData" in str(d) or "scoop" in str(d)]
            assert len(windows_dirs) > 0

    def test_get_search_directories_unix(self):
        """Test search directories on Unix systems."""
        with patch("sys.platform", "linux"):
            discovery = CLIToolDiscovery()
            dirs = discovery._get_search_directories()

            # Check for Unix-specific directories
            unix_dirs = [d for d in dirs if "/usr/" in str(d) or "/opt/" in str(d)]
            assert len(unix_dirs) > 0

    def test_find_executable(self):
        """Test finding executables in directory."""
        # Create a temporary directory with a mock executable
        test_dir = Path("/tmp/test_tools")
        test_dir.mkdir(exist_ok=True)

        with (
            patch("pathlib.Path.is_file", return_value=True),
            patch("os.access", return_value=True),
        ):

            result = self.discovery._find_executable(test_dir, "test_tool")
            expected = test_dir / "test_tool"
            assert result == expected

    def test_find_executable_with_extension(self):
        """Test finding executables with Windows extensions."""
        test_dir = Path("/tmp/test_tools")

        with (
            patch("sys.platform", "win32"),
            patch("pathlib.Path.is_file") as mock_is_file,
            patch("os.access", return_value=True),
        ):

            # Mock that .exe file exists
            mock_is_file.side_effect = lambda p: str(p).endswith(".exe")

            result = self.discovery._find_executable(test_dir, "test_tool")
            expected = test_dir / "test_tool.exe"
            assert result == expected

    def test_extract_version(self):
        """Test version extraction from tool output."""
        test_cases = [
            ("ruff 0.1.0", "0.1.0"),
            ("mypy version 1.5.0", "1.5.0"),
            ("v2.0.1", "2.0.1"),
            ("tool 3.2", "3.2"),
            ("No version info", None),
        ]

        for output, expected in test_cases:
            result = self.discovery._extract_version(output)
            assert result == expected

    @patch("subprocess.run")
    def test_test_tool_functionality_success(self, mock_run):
        """Test successful tool functionality testing."""
        # Mock successful subprocess run
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "test-tool version 1.0.0"
        mock_run.return_value = mock_result

        result = self.discovery.test_tool_functionality(
            "/usr/bin/test-tool", "test-tool"
        )

        assert result["working"] is True
        assert result["version"] == "1.0.0"
        assert result["path"] == "/usr/bin/test-tool"

    @patch("subprocess.run")
    def test_test_tool_functionality_failure(self, mock_run):
        """Test failed tool functionality testing."""
        # Mock failed subprocess run
        mock_run.side_effect = FileNotFoundError()

        result = self.discovery.test_tool_functionality(
            "/usr/bin/missing-tool", "missing-tool"
        )

        assert result["working"] is False
        assert result["version"] is None

    @patch("subprocess.run")
    def test_check_path_tools(self, mock_run):
        """Test checking tools in PATH."""
        # Mock successful 'which' command
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "/usr/bin/git\n"
        mock_run.return_value = mock_result

        with patch("sys.platform", "linux"):
            result = self.discovery.check_path_tools()

            # Should find git in PATH
            assert "git" in result
            assert result["git"] == "/usr/bin/git"

    def test_get_tool_category(self):
        """Test tool category detection."""
        assert self.discovery._get_tool_category("git") == "Development"
        assert self.discovery._get_tool_category("ruff") == "Python Quality"
        assert self.discovery._get_tool_category("claude") == "AI Tools"
        assert self.discovery._get_tool_category("unknown_tool") is None

    def test_generate_adapter_config(self):
        """Test adapter configuration generation."""
        # Set up mock working tools
        self.discovery.working_tools = {
            "git": {"path": "/usr/bin/git", "version": "2.39.0", "in_path": True},
            "ruff": {
                "path": "/home/user/.local/bin/ruff",
                "version": "0.1.0",
                "in_path": False,
            },
        }

        with (
            patch("pathlib.Path.write_text") as mock_write,
            patch("pathlib.Path.mkdir"),
        ):

            self.discovery.generate_adapter_config()

            # Check that write_text was called
            mock_write.assert_called_once()

            # Check the generated content includes tools not in PATH
            written_content = mock_write.call_args[0][0]
            assert "ruff:" in written_content
            assert "/home/user/.local/bin/ruff" in written_content

    def test_generate_json_report(self):
        """Test JSON report generation."""
        # Set up mock working tools
        self.discovery.working_tools = {
            "git": {
                "path": "/usr/bin/git",
                "version": "2.39.0",
                "in_path": True,
                "category": "Development",
            },
            "ruff": {
                "path": "/home/user/.local/bin/ruff",
                "version": "0.1.0",
                "in_path": False,
                "category": "Python Quality",
            },
        }

        with (
            patch("builtins.open", create=True) as mock_open,
            patch("json.dump") as mock_json_dump,
            patch("pathlib.Path.mkdir"),
        ):

            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            self.discovery.generate_json_report()

            # Check that JSON dump was called
            mock_json_dump.assert_called_once()

            # Check the structure of the dumped data
            dumped_data = mock_json_dump.call_args[0][0]
            assert "tool_count" in dumped_data
            assert "categories" in dumped_data
            assert "tools" in dumped_data
            assert dumped_data["tool_count"] == 2

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_scan_for_executables(self, mock_exists, mock_run):
        """Test scanning for executables."""
        # Mock directory exists
        mock_exists.return_value = True

        # Mock finding tools
        with patch.object(self.discovery, "_scan_directory") as mock_scan:
            mock_scan.return_value = {
                "git": "/usr/bin/git",
                "ruff": "/usr/local/bin/ruff",
            }

            result = self.discovery.scan_for_executables(["git", "ruff"])

            assert "git" in result
            assert "ruff" in result

    def test_discover_and_validate_tools_integration(self):
        """Test the complete discovery and validation process."""
        with (
            patch.object(self.discovery, "check_path_tools") as mock_path,
            patch.object(self.discovery, "scan_for_executables") as mock_scan,
            patch.object(self.discovery, "test_tool_functionality") as mock_test,
        ):

            # Mock the methods
            mock_path.return_value = {"git": "/usr/bin/git"}
            mock_scan.return_value = {"ruff": "/usr/local/bin/ruff"}
            mock_test.return_value = {"working": True, "version": "1.0.0"}

            result = self.discovery.discover_and_validate_tools()

            # Should have both tools
            assert len(result) == 2
            assert "git" in result
            assert "ruff" in result

    def test_empty_discovery_result(self):
        """Test handling of empty discovery results."""
        self.discovery.working_tools = {}

        with pytest.raises(ValueError, match="No working tools discovered"):
            self.discovery.generate_adapter_config()


class TestToolDiscoveryIntegration:
    """Integration tests for tool discovery."""

    def test_real_python_discovery(self):
        """Test discovering real Python executable."""
        discovery = CLIToolDiscovery()

        # Python should always be available in test environment
        path_tools = discovery.check_path_tools()

        # Should find python
        assert any(tool.startswith("python") for tool in path_tools.keys())

    def test_tool_category_completeness(self):
        """Test that all expected tool categories are present."""
        discovery = CLIToolDiscovery()
        categories = discovery.tool_categories

        expected_categories = [
            "AI Tools",
            "Development",
            "Python Quality",
            "Containers",
            "Build Tools",
            "Testing",
            "Shell Tools",
        ]

        for category in expected_categories:
            assert category in categories
            assert len(categories[category]) > 0

    def test_search_directory_existence(self):
        """Test that at least some search directories exist."""
        discovery = CLIToolDiscovery()

        # At least home directory should exist
        existing_dirs = [d for d in discovery.search_directories if d.exists()]
        assert len(existing_dirs) > 0
