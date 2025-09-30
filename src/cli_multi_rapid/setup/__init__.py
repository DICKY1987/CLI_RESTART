"""
CLI Orchestrator Setup Module

This module provides automated setup, tool discovery, and validation functionality
for the CLI Orchestrator system. It includes cross-platform tool detection,
configuration generation, and comprehensive system validation.
"""

from .platform_setup import PlatformSetup
from .tool_discovery import CLIToolDiscovery
from .validation import SystemValidator

__all__ = ["CLIToolDiscovery", "SystemValidator", "PlatformSetup"]
