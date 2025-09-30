"""
Platform-specific Setup and Configuration

Handles Windows and cross-platform setup functionality, including
PowerShell script generation and platform-specific tool configuration.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional

from rich.console import Console

console = Console()


class PlatformSetup:
    """Platform-specific setup and configuration manager."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize platform setup manager."""
        self.project_root = project_root or Path.cwd()
        self.platform = sys.platform
        self.is_windows = self.platform == "win32"

    def generate_windows_setup_script(
        self, discovered_tools: Dict[str, Dict], output_path: Optional[Path] = None
    ) -> Path:
        """Generate Windows PowerShell setup script."""
        if output_path is None:
            scripts_dir = self.project_root / "scripts" / "setup"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            output_path = scripts_dir / "windows_tool_setup.ps1"

        script_content = self._generate_powershell_script(discovered_tools)
        output_path.write_text(script_content, encoding="utf-8")

        console.print(
            f"[green]✅ Windows setup script generated: {output_path}[/green]"
        )
        return output_path

    def _generate_powershell_script(self, discovered_tools: Dict[str, Dict]) -> str:
        """Generate PowerShell script content for Windows setup."""
        tools_to_add = [
            tool_info
            for tool_info in discovered_tools.values()
            if not tool_info.get("in_path", False)
        ]

        script = f"""# CLI Orchestrator Windows Environment Setup
# Generated automatically - adds discovered tools to PATH

Write-Host "🔧 CLI Orchestrator Windows Setup" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
Write-Host

# Discovered tools summary
Write-Host "📊 Tools Summary:" -ForegroundColor Yellow
Write-Host "  Total tools: {len(discovered_tools)}"
Write-Host "  Tools in PATH: {sum(1 for t in discovered_tools.values() if t.get('in_path', False))}"
Write-Host "  Custom paths: {len(tools_to_add)}"
Write-Host

# Add tools to PATH for current session
$originalPath = $env:PATH
$toolDirectories = @()

"""

        # Add each tool directory
        for tool_name, tool_info in discovered_tools.items():
            if not tool_info.get("in_path", False):
                tool_dir = str(Path(tool_info["path"]).parent)
                script += f"""
# {tool_name} - Version: {tool_info.get("version", "unknown")}
$toolDir = "{tool_dir}"
if (Test-Path $toolDir) {{
    if ($env:PATH -notlike "*$toolDir*") {{
        $env:PATH += ";$toolDir"
        $toolDirectories += $toolDir
        Write-Host "  ✅ Added: {tool_name}" -ForegroundColor Green
    }}
}}
"""

        script += """
Write-Host
Write-Host "📁 Directories added to PATH:" -ForegroundColor Cyan
foreach ($dir in $toolDirectories) {
    Write-Host "  - $dir" -ForegroundColor Gray
}

Write-Host
Write-Host "🧪 Verifying tool accessibility..." -ForegroundColor Yellow

# Test each tool
$workingTools = @()
$failedTools = @()

"""

        # Add verification for each tool
        for tool_name in discovered_tools.keys():
            script += f"""
try {{
    $result = Get-Command {tool_name} -ErrorAction SilentlyContinue
    if ($result) {{
        $workingTools += "{tool_name}"
        Write-Host "  ✅ {tool_name} accessible" -ForegroundColor Green
    }} else {{
        $failedTools += "{tool_name}"
        Write-Host "  ❌ {tool_name} not accessible" -ForegroundColor Red
    }}
}} catch {{
    $failedTools += "{tool_name}"
    Write-Host "  ❌ {tool_name} error: $($_.Exception.Message)" -ForegroundColor Red
}}
"""

        script += """
Write-Host
Write-Host "📈 Setup Results:" -ForegroundColor Yellow
Write-Host "  Working tools: $($workingTools.Count)"
Write-Host "  Failed tools: $($failedTools.Count)"

if ($failedTools.Count -eq 0) {
    Write-Host
    Write-Host "🎉 All tools are now accessible!" -ForegroundColor Green
    Write-Host "You can now run CLI orchestrator commands." -ForegroundColor Green
} else {
    Write-Host
    Write-Host "⚠️  Some tools are still not accessible:" -ForegroundColor Yellow
    foreach ($tool in $failedTools) {
        Write-Host "  - $tool" -ForegroundColor Red
    }
}

Write-Host
Write-Host "📝 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Test CLI: python -m cli_multi_rapid.main --help"
Write-Host "2. Run doctor: python -m cli_multi_rapid.main tools doctor"
Write-Host "3. Validate setup: python -m cli_multi_rapid.main setup validate"

# Note: This only affects the current PowerShell session
Write-Host
Write-Host "💡 Note: PATH changes apply only to this session." -ForegroundColor Yellow
Write-Host "   For permanent changes, update your system PATH or user profile." -ForegroundColor Yellow
"""

        return script

    def generate_environment_setup(
        self, discovered_tools: Dict[str, Dict], output_path: Optional[Path] = None
    ) -> Path:
        """Generate cross-platform environment setup."""
        if output_path is None:
            scripts_dir = self.project_root / "scripts" / "setup"
            scripts_dir.mkdir(parents=True, exist_ok=True)

            if self.is_windows:
                output_path = scripts_dir / "setup_environment.ps1"
                content = self._generate_windows_env_setup(discovered_tools)
            else:
                output_path = scripts_dir / "setup_environment.sh"
                content = self._generate_unix_env_setup(discovered_tools)

        output_path.write_text(content, encoding="utf-8")

        # Make executable on Unix systems
        if not self.is_windows:
            os.chmod(output_path, 0o755)

        console.print(
            f"[green]✅ Environment setup script generated: {output_path}[/green]"
        )
        return output_path

    def _generate_windows_env_setup(self, discovered_tools: Dict[str, Dict]) -> str:
        """Generate Windows environment setup script."""
        custom_tools = {
            name: info
            for name, info in discovered_tools.items()
            if not info.get("in_path", False)
        }

        script = f"""# CLI Orchestrator Environment Setup (Windows)
# Adds discovered tools to current session PATH

Write-Host "🔧 Setting up CLI Orchestrator environment..." -ForegroundColor Green

# Tools to add ({len(custom_tools)} custom paths)
$toolPaths = @(
"""

        for tool_name, tool_info in custom_tools.items():
            tool_dir = str(Path(tool_info["path"]).parent)
            script += f'    "{tool_dir}",  # {tool_name}\n'

        script += """)

# Add unique directories to PATH
$addedPaths = @()
foreach ($path in $toolPaths) {
    if ((Test-Path $path) -and ($env:PATH -notlike "*$path*")) {
        $env:PATH += ";$path"
        $addedPaths += $path
    }
}

Write-Host "✅ Added $($addedPaths.Count) directories to PATH" -ForegroundColor Green
Write-Host "🧪 Testing CLI Orchestrator..." -ForegroundColor Yellow

try {
    $result = python -m cli_multi_rapid.main --help 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ CLI Orchestrator is working!" -ForegroundColor Green
    } else {
        Write-Host "❌ CLI Orchestrator test failed" -ForegroundColor Red
        Write-Host $result -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error testing CLI Orchestrator: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host
Write-Host "🚀 Environment setup complete!" -ForegroundColor Green
Write-Host "Run 'python -m cli_multi_rapid.main tools doctor' to verify all tools." -ForegroundColor Cyan
"""

        return script

    def _generate_unix_env_setup(self, discovered_tools: Dict[str, Dict]) -> str:
        """Generate Unix/Linux environment setup script."""
        custom_tools = {
            name: info
            for name, info in discovered_tools.items()
            if not info.get("in_path", False)
        }

        script = f"""#!/bin/bash
# CLI Orchestrator Environment Setup (Unix/Linux)
# Adds discovered tools to current session PATH

echo "🔧 Setting up CLI Orchestrator environment..."

# Tools to add ({len(custom_tools)} custom paths)
TOOL_PATHS=(
"""

        for tool_name, tool_info in custom_tools.items():
            tool_dir = str(Path(tool_info["path"]).parent)
            script += f'    "{tool_dir}"  # {tool_name}\n'

        script += """)

# Add unique directories to PATH
ADDED_PATHS=()
for path in "${TOOL_PATHS[@]}"; do
    if [[ -d "$path" && ":$PATH:" != *":$path:"* ]]; then
        export PATH="$PATH:$path"
        ADDED_PATHS+=("$path")
    fi
done

echo "✅ Added ${#ADDED_PATHS[@]} directories to PATH"
echo "🧪 Testing CLI Orchestrator..."

if python -m cli_multi_rapid.main --help >/dev/null 2>&1; then
    echo "✅ CLI Orchestrator is working!"
else
    echo "❌ CLI Orchestrator test failed"
fi

echo
echo "🚀 Environment setup complete!"
echo "Run 'python -m cli_multi_rapid.main tools doctor' to verify all tools."
"""

        return script

    def create_platform_config(self, discovered_tools: Dict[str, Dict]) -> Dict:
        """Create platform-specific configuration."""
        config = {
            "platform": self.platform,
            "is_windows": self.is_windows,
            "tool_count": len(discovered_tools),
            "platform_specific_tools": {},
            "environment_variables": {},
            "recommendations": [],
        }

        # Platform-specific recommendations
        if self.is_windows:
            config["recommendations"].extend(
                [
                    "Use PowerShell for best compatibility",
                    "Consider using Windows Terminal for better Unicode support",
                    "Install Git for Windows if not already installed",
                    "Consider using scoop or chocolatey for tool management",
                ]
            )

            # Windows-specific tool paths
            for tool_name, tool_info in discovered_tools.items():
                if "Windows" in tool_info.get("path", "") or "AppData" in tool_info.get(
                    "path", ""
                ):
                    config["platform_specific_tools"][tool_name] = tool_info

        else:
            config["recommendations"].extend(
                [
                    "Use bash or zsh for best compatibility",
                    "Consider using homebrew for tool management",
                    "Ensure Python 3.9+ is installed via system package manager",
                ]
            )

            # Unix-specific tool paths
            for tool_name, tool_info in discovered_tools.items():
                path = tool_info.get("path", "")
                if any(
                    unix_path in path for unix_path in ["/usr/local", "/opt", "/.local"]
                ):
                    config["platform_specific_tools"][tool_name] = tool_info

        return config

    def generate_installer_script(self, output_path: Optional[Path] = None) -> Path:
        """Generate platform-specific installer script."""
        if output_path is None:
            scripts_dir = self.project_root / "scripts" / "setup"
            scripts_dir.mkdir(parents=True, exist_ok=True)

            if self.is_windows:
                output_path = scripts_dir / "install_cli_orchestrator.ps1"
                content = self._generate_windows_installer()
            else:
                output_path = scripts_dir / "install_cli_orchestrator.sh"
                content = self._generate_unix_installer()

        output_path.write_text(content, encoding="utf-8")

        if not self.is_windows:
            os.chmod(output_path, 0o755)

        console.print(f"[green]✅ Installer script generated: {output_path}[/green]")
        return output_path

    def _generate_windows_installer(self) -> str:
        """Generate Windows installer script."""
        return """# CLI Orchestrator Windows Installer
# Automated installation and setup

param(
    [switch]$DryRun,
    [switch]$SkipTools
)

Write-Host "🚀 CLI Orchestrator Windows Installer" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No changes will be made" -ForegroundColor Yellow
}

# Check Python
Write-Host "🐍 Checking Python installation..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Python not found. Please install Python 3.9+ first." -ForegroundColor Red
    exit 1
}

# Install CLI Orchestrator
Write-Host "📦 Installing CLI Orchestrator..." -ForegroundColor Cyan
if (-not $DryRun) {
    pip install -e .[dev,ai]
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ CLI Orchestrator installed successfully" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Installation failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  🔍 Would run: pip install -e .[dev,ai]" -ForegroundColor Yellow
}

# Discover tools
if (-not $SkipTools) {
    Write-Host "🔍 Discovering tools..." -ForegroundColor Cyan
    if (-not $DryRun) {
        python -m cli_multi_rapid.main tools setup --discover
    } else {
        Write-Host "  🔍 Would run tool discovery" -ForegroundColor Yellow
    }
}

# Validate installation
Write-Host "🧪 Validating installation..." -ForegroundColor Cyan
if (-not $DryRun) {
    python -m cli_multi_rapid.main setup validate
} else {
    Write-Host "  🔍 Would run validation" -ForegroundColor Yellow
}

Write-Host
Write-Host "🎉 Installation complete!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Run: python -m cli_multi_rapid.main --help" -ForegroundColor White
Write-Host "  2. Test: python -m cli_multi_rapid.main tools doctor" -ForegroundColor White
"""

    def _generate_unix_installer(self) -> str:
        """Generate Unix/Linux installer script."""
        return """#!/bin/bash
# CLI Orchestrator Unix/Linux Installer
# Automated installation and setup

set -e

DRY_RUN=false
SKIP_TOOLS=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-tools)
            SKIP_TOOLS=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "🚀 CLI Orchestrator Unix/Linux Installer"
echo "========================================"

if [ "$DRY_RUN" = true ]; then
    echo "🔍 DRY RUN MODE - No changes will be made"
fi

# Check Python
echo "🐍 Checking Python installation..."
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version)
    echo "  ✅ Found: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_VERSION=$(python --version)
    echo "  ✅ Found: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    echo "  ❌ Python not found. Please install Python 3.9+ first."
    exit 1
fi

# Install CLI Orchestrator
echo "📦 Installing CLI Orchestrator..."
if [ "$DRY_RUN" = false ]; then
    pip install -e .[dev,ai]
    echo "  ✅ CLI Orchestrator installed successfully"
else
    echo "  🔍 Would run: pip install -e .[dev,ai]"
fi

# Discover tools
if [ "$SKIP_TOOLS" = false ]; then
    echo "🔍 Discovering tools..."
    if [ "$DRY_RUN" = false ]; then
        $PYTHON_CMD -m cli_multi_rapid.main tools setup --discover
    else
        echo "  🔍 Would run tool discovery"
    fi
fi

# Validate installation
echo "🧪 Validating installation..."
if [ "$DRY_RUN" = false ]; then
    $PYTHON_CMD -m cli_multi_rapid.main setup validate
else
    echo "  🔍 Would run validation"
fi

echo
echo "🎉 Installation complete!"
echo "Next steps:"
echo "  1. Run: $PYTHON_CMD -m cli_multi_rapid.main --help"
echo "  2. Test: $PYTHON_CMD -m cli_multi_rapid.main tools doctor"
"""
