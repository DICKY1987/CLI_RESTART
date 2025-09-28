"""
Tests for Platform Setup functionality.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from cli_multi_rapid.setup.platform_setup import PlatformSetup


class TestPlatformSetup:
    """Test cases for PlatformSetup class."""

    def setup_method(self):
        """Set up test instance."""
        self.platform_setup = PlatformSetup()

    def test_initialization(self):
        """Test PlatformSetup initialization."""
        assert self.platform_setup.project_root == Path.cwd()
        assert self.platform_setup.platform == sys.platform
        assert isinstance(self.platform_setup.is_windows, bool)

    def test_custom_project_root(self):
        """Test initialization with custom project root."""
        custom_root = Path("/custom/project")
        setup = PlatformSetup(project_root=custom_root)
        assert setup.project_root == custom_root

    def test_windows_detection(self):
        """Test Windows platform detection."""
        with patch("sys.platform", "win32"):
            setup = PlatformSetup()
            assert setup.is_windows is True
            assert setup.platform == "win32"

    def test_unix_detection(self):
        """Test Unix platform detection."""
        with patch("sys.platform", "linux"):
            setup = PlatformSetup()
            assert setup.is_windows is False
            assert setup.platform == "linux"

    def test_generate_powershell_script_content(self):
        """Test PowerShell script content generation."""
        mock_tools = {
            "ruff": {
                "path": "C:\\Users\\Test\\.local\\bin\\ruff.exe",
                "version": "0.1.0",
                "in_path": False,
            },
            "git": {
                "path": "C:\\Program Files\\Git\\bin\\git.exe",
                "version": "2.39.0",
                "in_path": True,
            },
        }

        script_content = self.platform_setup._generate_powershell_script(mock_tools)

        # Check that script contains expected elements
        assert "CLI Orchestrator Windows Setup" in script_content
        assert "ruff" in script_content
        assert "C:\\Users\\Test\\.local\\bin" in script_content
        # Git should not be added to PATH since it's already there
        assert "Program Files\\Git" not in script_content

    def test_generate_windows_setup_script(self):
        """Test Windows setup script generation."""
        mock_tools = {
            "ruff": {
                "path": "C:\\tools\\ruff.exe",
                "version": "0.1.0",
                "in_path": False,
            }
        }

        with (
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.write_text") as mock_write,
        ):

            result_path = self.platform_setup.generate_windows_setup_script(mock_tools)

            mock_write.assert_called_once()
            written_content = mock_write.call_args[0][0]
            assert "PowerShell" in written_content
            assert "ruff" in written_content

    def test_generate_windows_env_setup(self):
        """Test Windows environment setup script generation."""
        mock_tools = {
            "tool1": {"path": "C:\\custom\\tool1.exe", "in_path": False},
            "tool2": {"path": "C:\\another\\tool2.exe", "in_path": False},
            "git": {"path": "C:\\Program Files\\Git\\bin\\git.exe", "in_path": True},
        }

        script_content = self.platform_setup._generate_windows_env_setup(mock_tools)

        # Should only include tools not in PATH
        assert "C:\\custom" in script_content
        assert "C:\\another" in script_content
        assert "Program Files\\Git" not in script_content
        assert "$env:PATH" in script_content

    def test_generate_unix_env_setup(self):
        """Test Unix environment setup script generation."""
        mock_tools = {
            "tool1": {"path": "/home/user/.local/bin/tool1", "in_path": False},
            "tool2": {"path": "/opt/custom/tool2", "in_path": False},
            "git": {"path": "/usr/bin/git", "in_path": True},
        }

        script_content = self.platform_setup._generate_unix_env_setup(mock_tools)

        # Should only include tools not in PATH
        assert "/home/user/.local/bin" in script_content
        assert "/opt/custom" in script_content
        assert "/usr/bin" not in script_content
        assert "export PATH" in script_content
        assert "#!/bin/bash" in script_content

    def test_generate_environment_setup_windows(self):
        """Test environment setup generation for Windows."""
        mock_tools = {"tool1": {"path": "C:\\tools\\tool1.exe", "in_path": False}}

        with (
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.write_text") as mock_write,
            patch("sys.platform", "win32"),
        ):

            result_path = self.platform_setup.generate_environment_setup(mock_tools)

            mock_write.assert_called_once()
            assert result_path.suffix == ".ps1"
            written_content = mock_write.call_args[0][0]
            assert "PowerShell" in written_content

    def test_generate_environment_setup_unix(self):
        """Test environment setup generation for Unix."""
        mock_tools = {"tool1": {"path": "/usr/local/bin/tool1", "in_path": False}}

        with (
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.write_text") as mock_write,
            patch("os.chmod") as mock_chmod,
            patch("sys.platform", "linux"),
        ):

            result_path = self.platform_setup.generate_environment_setup(mock_tools)

            mock_write.assert_called_once()
            mock_chmod.assert_called_once()
            assert result_path.suffix == ".sh"
            written_content = mock_write.call_args[0][0]
            assert "#!/bin/bash" in written_content

    def test_create_platform_config_windows(self):
        """Test platform configuration creation for Windows."""
        mock_tools = {
            "tool1": {"path": "C:\\Users\\Test\\AppData\\Local\\tool1.exe"},
            "tool2": {"path": "C:\\Program Files\\tool2.exe"},
        }

        with patch("sys.platform", "win32"):
            setup = PlatformSetup()
            config = setup.create_platform_config(mock_tools)

            assert config["platform"] == "win32"
            assert config["is_windows"] is True
            assert "PowerShell" in str(config["recommendations"])
            assert len(config["platform_specific_tools"]) > 0

    def test_create_platform_config_unix(self):
        """Test platform configuration creation for Unix."""
        mock_tools = {
            "tool1": {"path": "/usr/local/bin/tool1"},
            "tool2": {"path": "/opt/homebrew/bin/tool2"},
        }

        with patch("sys.platform", "linux"):
            setup = PlatformSetup()
            config = setup.create_platform_config(mock_tools)

            assert config["platform"] == "linux"
            assert config["is_windows"] is False
            assert "bash" in str(config["recommendations"])
            assert len(config["platform_specific_tools"]) > 0

    def test_generate_windows_installer(self):
        """Test Windows installer script generation."""
        installer_content = self.platform_setup._generate_windows_installer()

        assert "CLI Orchestrator Windows Installer" in installer_content
        assert "param(" in installer_content
        assert "pip install -e .[dev,ai]" in installer_content
        assert "$DryRun" in installer_content

    def test_generate_unix_installer(self):
        """Test Unix installer script generation."""
        installer_content = self.platform_setup._generate_unix_installer()

        assert "CLI Orchestrator Unix/Linux Installer" in installer_content
        assert "#!/bin/bash" in installer_content
        assert "pip install -e .[dev,ai]" in installer_content
        assert "--dry-run" in installer_content

    def test_generate_installer_script_windows(self):
        """Test installer script generation for Windows."""
        with (
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.write_text") as mock_write,
            patch("sys.platform", "win32"),
        ):

            setup = PlatformSetup()
            result_path = setup.generate_installer_script()

            mock_write.assert_called_once()
            assert result_path.suffix == ".ps1"
            written_content = mock_write.call_args[0][0]
            assert "Windows Installer" in written_content

    def test_generate_installer_script_unix(self):
        """Test installer script generation for Unix."""
        with (
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.write_text") as mock_write,
            patch("os.chmod") as mock_chmod,
            patch("sys.platform", "linux"),
        ):

            setup = PlatformSetup()
            result_path = setup.generate_installer_script()

            mock_write.assert_called_once()
            mock_chmod.assert_called_once()
            assert result_path.suffix == ".sh"
            written_content = mock_write.call_args[0][0]
            assert "Unix/Linux Installer" in written_content

    def test_empty_tools_handling(self):
        """Test handling of empty tools dictionary."""
        empty_tools = {}

        script_content = self.platform_setup._generate_powershell_script(empty_tools)
        assert "Total tools: 0" in script_content

        script_content = self.platform_setup._generate_windows_env_setup(empty_tools)
        assert "custom paths: 0" in script_content

    def test_path_normalization(self):
        """Test path normalization in scripts."""
        tools_with_paths = {
            "tool1": {"path": "C:\\Users\\Test\\My Tools\\tool1.exe", "in_path": False}
        }

        script_content = self.platform_setup._generate_powershell_script(
            tools_with_paths
        )

        # Should handle paths with spaces correctly
        assert "My Tools" in script_content
        assert "$toolDir" in script_content

    def test_tool_filtering_by_path_status(self):
        """Test that only tools not in PATH are included in setup scripts."""
        mixed_tools = {
            "in_path_tool": {"path": "/usr/bin/tool1", "in_path": True},
            "custom_tool": {"path": "/home/user/.local/bin/tool2", "in_path": False},
        }

        # Windows environment setup
        windows_content = self.platform_setup._generate_windows_env_setup(mixed_tools)
        assert "tool2" in windows_content
        assert "tool1" not in windows_content

        # Unix environment setup
        unix_content = self.platform_setup._generate_unix_env_setup(mixed_tools)
        assert "/home/user/.local/bin" in unix_content
        assert "/usr/bin" not in unix_content


class TestPlatformSetupIntegration:
    """Integration tests for platform setup."""

    def test_real_platform_detection(self):
        """Test platform detection with real system."""
        setup = PlatformSetup()

        # Should correctly detect current platform
        assert setup.platform == sys.platform
        if sys.platform == "win32":
            assert setup.is_windows is True
        else:
            assert setup.is_windows is False

    def test_script_generation_with_real_paths(self):
        """Test script generation with realistic path structures."""
        # Create realistic tool paths for current platform
        if sys.platform == "win32":
            tools = {
                "python": {"path": "C:\\Python311\\python.exe", "in_path": True},
                "custom_tool": {
                    "path": "C:\\Users\\Test\\AppData\\Local\\Programs\\custom\\tool.exe",
                    "in_path": False,
                },
            }
        else:
            tools = {
                "python": {"path": "/usr/bin/python3", "in_path": True},
                "custom_tool": {
                    "path": "/home/user/.local/bin/custom_tool",
                    "in_path": False,
                },
            }

        setup = PlatformSetup()

        # Should generate script without errors
        try:
            if setup.is_windows:
                script_content = setup._generate_powershell_script(tools)
                assert len(script_content) > 100
            else:
                script_content = setup._generate_unix_env_setup(tools)
                assert len(script_content) > 100
        except Exception as e:
            pytest.fail(f"Script generation failed: {e}")

    def test_file_operations_mocked(self):
        """Test file operations with proper mocking."""
        tools = {"test_tool": {"path": "/test/path", "in_path": False}}

        with (
            patch("pathlib.Path.mkdir") as mock_mkdir,
            patch("pathlib.Path.write_text") as mock_write,
            patch("os.chmod") as mock_chmod,
        ):

            setup = PlatformSetup()

            # Test environment setup
            result_path = setup.generate_environment_setup(tools)
            mock_mkdir.assert_called()
            mock_write.assert_called()

            # Test installer generation
            installer_path = setup.generate_installer_script()
            assert mock_write.call_count >= 2  # Called for both scripts

            # On Unix, chmod should be called
            if not setup.is_windows:
                assert mock_chmod.call_count >= 2

    def test_platform_config_structure(self):
        """Test platform configuration structure completeness."""
        tools = {
            "tool1": {"path": "/some/path/tool1", "category": "Development"},
            "tool2": {"path": "/another/path/tool2", "category": "Testing"},
        }

        setup = PlatformSetup()
        config = setup.create_platform_config(tools)

        # Check required fields
        required_fields = [
            "platform",
            "is_windows",
            "tool_count",
            "platform_specific_tools",
            "environment_variables",
            "recommendations",
        ]

        for field in required_fields:
            assert field in config, f"Missing required field: {field}"

        # Check data types
        assert isinstance(config["platform"], str)
        assert isinstance(config["is_windows"], bool)
        assert isinstance(config["tool_count"], int)
        assert isinstance(config["platform_specific_tools"], dict)
        assert isinstance(config["environment_variables"], dict)
        assert isinstance(config["recommendations"], list)

        # Check values make sense
        assert config["tool_count"] == len(tools)
        assert len(config["recommendations"]) > 0
