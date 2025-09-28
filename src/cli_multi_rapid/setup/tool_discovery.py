"""
CLI Tool Discovery and Configuration System

Automatically discovers and configures CLI tools for the orchestrator system.
Supports cross-platform tool detection with Windows-specific enhancements.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class CLIToolDiscovery:
    """Automated CLI tool discovery and configuration system."""

    def __init__(self, home_dir: Optional[Path] = None):
        """Initialize tool discovery system."""
        self.home_dir = home_dir or Path.home()
        self.discovered_tools: Dict[str, Dict] = {}
        self.working_tools: Dict[str, Dict] = {}

        # Tool categories for organized discovery
        self.tool_categories = {
            "AI Tools": ["claude", "aider", "cursor", "copilot", "openai", "gemini"],
            "Development": [
                "git",
                "gh",
                "code",
                "node",
                "npm",
                "npx",
                "python",
                "pip",
                "pipx",
            ],
            "Python Quality": [
                "ruff",
                "mypy",
                "black",
                "isort",
                "bandit",
                "semgrep",
                "pylint",
                "flake8",
            ],
            "Containers": ["docker", "docker-compose", "podman"],
            "Build Tools": ["make", "cmake", "msbuild", "ninja"],
            "Testing": ["pytest", "coverage", "tox", "nox"],
            "Shell Tools": ["curl", "wget", "jq", "yq"],
        }

        # Search directories (cross-platform)
        self.search_directories = self._get_search_directories()

    def _get_search_directories(self) -> List[Path]:
        """Get platform-specific search directories."""
        dirs = [
            self.home_dir,
            self.home_dir / "bin",
            self.home_dir / ".local" / "bin",
        ]

        if sys.platform == "win32":
            # Windows-specific directories
            dirs.extend(
                [
                    self.home_dir / "AppData" / "Local" / "Programs",
                    self.home_dir / "AppData" / "Roaming" / "npm",
                    self.home_dir / ".cargo" / "bin",
                    self.home_dir / ".gem" / "bin",
                    self.home_dir / "go" / "bin",
                    self.home_dir / ".bun" / "bin",
                    self.home_dir / ".ollama" / "bin",
                    self.home_dir / ".ai" / "bin",
                    self.home_dir / "scoop" / "shims",
                    Path("C:/ProgramData/chocolatey/bin"),
                    Path("C:/tools"),
                    Path(os.environ.get("LOCALAPPDATA", ""))
                    / "Microsoft"
                    / "WindowsApps",
                ]
            )
        else:
            # Unix-like systems
            dirs.extend(
                [
                    Path("/usr/local/bin"),
                    Path("/usr/bin"),
                    Path("/opt/homebrew/bin"),  # macOS with Apple Silicon
                    Path("/home/linuxbrew/.linuxbrew/bin"),  # Linux with Homebrew
                ]
            )

        return [d for d in dirs if d.exists()]

    def scan_for_executables(
        self, tool_names: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Scan directories for executable tools."""
        if tool_names is None:
            tool_names = [
                tool for tools in self.tool_categories.values() for tool in tools
            ]

        found_tools = {}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "Scanning for tools...", total=len(self.search_directories)
            )

            for directory in self.search_directories:
                progress.update(task, description=f"Scanning: {directory}")
                found_in_dir = self._scan_directory(directory, tool_names)
                found_tools.update(found_in_dir)
                progress.advance(task)

        return found_tools

    def _scan_directory(self, directory: Path, tool_names: List[str]) -> Dict[str, str]:
        """Scan a specific directory for tools."""
        found = {}

        if not directory.exists():
            return found

        try:
            for tool_name in tool_names:
                tool_path = self._find_executable(directory, tool_name)
                if tool_path and tool_name not in found:
                    found[tool_name] = str(tool_path)
        except (PermissionError, OSError):
            # Skip directories we can't access
            pass

        return found

    def _find_executable(self, directory: Path, tool_name: str) -> Optional[Path]:
        """Find executable in directory with platform-specific extensions."""
        extensions = [""]
        if sys.platform == "win32":
            extensions = [".exe", ".cmd", ".bat", ".ps1"]

        for ext in extensions:
            tool_path = directory / f"{tool_name}{ext}"
            if tool_path.is_file() and os.access(tool_path, os.X_OK):
                return tool_path

        return None

    def test_tool_functionality(self, tool_path: str, tool_name: str) -> Dict:
        """Test if a tool works and get version information."""
        version_commands = ["--version", "-v", "--help", "-h"]

        for cmd in version_commands:
            try:
                result = subprocess.run(
                    [tool_path, cmd],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                )

                if result.returncode == 0 or "version" in result.stdout.lower():
                    version = self._extract_version(result.stdout)
                    return {
                        "working": True,
                        "version": version,
                        "path": tool_path,
                        "output": result.stdout,
                    }
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue

        return {
            "working": False,
            "version": None,
            "path": tool_path,
            "output": "No response",
        }

    def _extract_version(self, output: str) -> Optional[str]:
        """Extract version number from tool output."""
        import re

        # Common version patterns
        patterns = [
            r"version\s+(\d+\.\d+(?:\.\d+)?)",
            r"v(\d+\.\d+(?:\.\d+)?)",
            r"(\d+\.\d+(?:\.\d+)?)",
        ]

        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def check_path_tools(self) -> Dict[str, str]:
        """Check which tools are available in PATH."""
        all_tools = [tool for tools in self.tool_categories.values() for tool in tools]
        path_tools = {}

        for tool in all_tools:
            try:
                # Use 'where' on Windows, 'which' on Unix
                cmd = "where" if sys.platform == "win32" else "which"
                result = subprocess.run(
                    [cmd, tool], capture_output=True, text=True, check=True
                )
                if result.stdout.strip():
                    path_tools[tool] = result.stdout.strip().split("\n")[0]
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

        return path_tools

    def discover_and_validate_tools(self) -> Dict[str, Dict]:
        """Complete tool discovery and validation process."""
        console.print(
            "[bold blue]🔍 Starting comprehensive tool discovery...[/bold blue]"
        )

        # Step 1: Check PATH tools
        console.print("📋 Checking tools in PATH...")
        path_tools = self.check_path_tools()
        console.print(f"Found {len(path_tools)} tools in PATH")

        # Step 2: Scan directories
        console.print("🏠 Scanning directories for additional tools...")
        discovered = self.scan_for_executables()

        # Combine results, preferring PATH tools
        all_found = {**discovered, **path_tools}
        console.print(f"Total tools found: {len(all_found)}")

        # Step 3: Test functionality
        console.print("🧪 Testing tool functionality...")
        working_tools = {}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Testing tools...", total=len(all_found))

            for tool_name, tool_path in all_found.items():
                progress.update(task, description=f"Testing {tool_name}...")
                test_result = self.test_tool_functionality(tool_path, tool_name)

                if test_result["working"]:
                    working_tools[tool_name] = {
                        "path": tool_path,
                        "version": test_result["version"],
                        "in_path": tool_name in path_tools,
                        "category": self._get_tool_category(tool_name),
                    }

                progress.advance(task)

        self.working_tools = working_tools
        console.print(
            f"[green]✅ {len(working_tools)} tools are working properly[/green]"
        )

        return working_tools

    def _get_tool_category(self, tool_name: str) -> Optional[str]:
        """Get the category for a tool."""
        for category, tools in self.tool_categories.items():
            if tool_name in tools:
                return category
        return None

    def generate_adapter_config(self, output_path: Optional[Path] = None) -> Path:
        """Generate CLI orchestrator adapter configuration."""
        if not self.working_tools:
            raise ValueError(
                "No working tools discovered. Run discover_and_validate_tools() first."
            )

        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)

        if output_path is None:
            output_path = config_dir / "discovered_tools.yaml"

        # Generate YAML configuration
        yaml_content = f"""# CLI Orchestrator Tool Configuration
# Generated automatically on {self._get_timestamp()}
# Total working tools: {len(self.working_tools)}

vcs: git
containers: docker
editor: code
js_runtime: node
ai_cli: claude
python_quality:
  ruff: {self.working_tools.get('ruff') is not None}
  mypy: {self.working_tools.get('mypy') is not None}
  bandit: {self.working_tools.get('bandit') is not None}
  semgrep: {self.working_tools.get('semgrep') is not None}
precommit: {self.working_tools.get('pre-commit') is not None}

paths:
"""

        # Add explicit paths for tools not in PATH
        for tool_name, tool_info in self.working_tools.items():
            if not tool_info["in_path"]:
                yaml_content += f'  {tool_name}: "{tool_info["path"]}"\n'

        output_path.write_text(yaml_content, encoding="utf-8")
        console.print(f"[green]✅ Configuration written to {output_path}[/green]")

        return output_path

    def generate_json_report(self, output_path: Optional[Path] = None) -> Path:
        """Generate detailed JSON report of discovered tools."""
        if output_path is None:
            output_path = Path("artifacts") / "discovered_tools.json"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "discovered_at": self._get_timestamp(),
            "tool_count": len(self.working_tools),
            "categories": {},
            "tools": {},
        }

        # Organize by categories
        for category, tools_in_category in self.tool_categories.items():
            found_in_category = [
                tool for tool in tools_in_category if tool in self.working_tools
            ]
            if found_in_category:
                report["categories"][category] = found_in_category

        # Add detailed tool information
        for tool_name, tool_info in self.working_tools.items():
            report["tools"][tool_name] = {
                "path": tool_info["path"],
                "version": tool_info["version"],
                "in_path": tool_info["in_path"],
                "category": tool_info["category"],
            }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        console.print(f"[green]✅ JSON report written to {output_path}[/green]")
        return output_path

    def print_discovery_summary(self):
        """Print a formatted summary of discovered tools."""
        if not self.working_tools:
            console.print("[yellow]No tools discovered yet[/yellow]")
            return

        console.print("\n[bold green]📊 DISCOVERY SUMMARY[/bold green]")
        console.print("=" * 50)

        for category, tools_in_category in self.tool_categories.items():
            found_tools = [
                tool for tool in tools_in_category if tool in self.working_tools
            ]

            if found_tools:
                console.print(
                    f"\n[bold cyan]📁 {category} ({len(found_tools)} tools)[/bold cyan]"
                )
                for tool in found_tools:
                    tool_info = self.working_tools[tool]
                    version = (
                        f" v{tool_info['version']}" if tool_info["version"] else ""
                    )
                    location = (
                        " (in PATH)" if tool_info["in_path"] else " (custom path)"
                    )
                    console.print(f"  ✅ {tool}{version}{location}")

        # Summary statistics
        path_count = sum(1 for t in self.working_tools.values() if t["in_path"])
        custom_count = len(self.working_tools) - path_count

        console.print("\n[bold yellow]📈 TOTALS:[/bold yellow]")
        console.print(f"  Working tools: {len(self.working_tools)}")
        console.print(f"  Tools in PATH: {path_count}")
        console.print(f"  Custom paths: {custom_count}")

    def _get_timestamp(self) -> str:
        """Get current timestamp for configuration files."""
        from datetime import datetime

        return datetime.now().isoformat()
